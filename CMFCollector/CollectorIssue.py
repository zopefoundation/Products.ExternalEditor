##############################################################################
# Copyright (c) 2001 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 1.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
##############################################################################

"""Implement the Collector Issue content type - a bundle containing the
collector transcript and various parts."""

import os, urllib, string, re
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base

import util                             # Collector utilities.

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.Document import addDocument

# Import permission names
from Products.CMFCore import CMFCorePermissions
from CollectorPermissions import *

urlchars  = (r'[A-Za-z0-9/:@_%~#=&\.\-\?]+')
nonpuncurlchars  = (r'[A-Za-z0-9/:@_%~#=&\-]')
url       = (r'["=]?((http|https|ftp|mailto|file|about):%s%s)'
             % (urlchars, nonpuncurlchars))
urlexp    = re.compile(url)
UPLOAD_PREFIX = "Uploaded: "
uploadexp = re.compile('(%s)([^<,\n]*)([<,\n])' % UPLOAD_PREFIX, re.MULTILINE)

DEFAULT_TRANSCRIPT_FORMAT = 'stx'

factory_type_information = (
    {'id': 'Collector Issue',
     'content_icon': 'collector_issue_icon.gif',
     'meta_type': 'CMF Collector Issue',
     'description': ('A Collector Issue represents a bug report or'
                     ' other support request.'),
     'product': 'CMFCollector',
     'factory': None,                   # So not included in 'New' add form
     'allowed_content_types': ('Collector Issue Transcript', 'File', 'Image'), 
     'immediate_view': 'collector_edit_form',
     'actions': ({'id': 'view',
                  'name': 'View Issue',
                  'action': 'collector_issue_contents',
                  'permissions': (ViewCollector,)},
                 {'id': 'followup',
                  'name': 'Followup',
                  'action': 'collector_issue_followup_form',
                  'permissions': (AddCollectorIssueFollowup,)},
                 {'id': 'edit',
                  'name': 'Edit Issue',
                  'action': 'collector_issue_edit_form',
                  'permissions': (EditCollectorIssue,)},
                 {'id': 'browse',
                  'name': 'Browse Collector',
                  'action': 'collector_issue_up',
                  'permissions': (ViewCollector,)},
                 {'id': 'addIssue',
                  'name': 'New Issue',
                  'action': 'collector_issue_add_issue',
                  'permissions': (ViewCollector,)},
                 ),
     },
    )

TRANSCRIPT_NAME = "ISSUE_TRANSCRIPT"

class CollectorIssue(SkinnedFolder, DefaultDublinCoreImpl):
    """An individual support request in the CMF Collector."""

    meta_type = 'CMF Collector Issue'
    effective_date = expiration_date = None
    
    security = ClassSecurityInfo()

    comment_delimiter = "<hr solid id=comment_delim>"

    action_number = 0

    ACTIONS_ORDER = ['Accept', 'Resign', 'Assign',
                     'Resolve', 'Reject', 'Defer'] 

    _collector_path = None

    def __init__(self,
                 id, container,
                 title='', description='',
                 submitter_id=None, submitter_name=None,
                 kibitzers=None,
                 topic=None, classification=None,
                 security_related=0,
                 importance=None, severity=None,
                 resolution=None,
                 reported_version=None, other_version_info=None,
                 creation_date=None, modification_date=None,
                 effective_date=None, expiration_date=None,
                 assignees=None,
                 file=None, fileid=None, filetype=None):
        """ """

        SkinnedFolder.__init__(self, id, title)
        self._set_collector_path(container)

        user = getSecurityManager().getUser()
        if submitter_id is None:
            submitter_id = str(user)
        self.submitter_id = submitter_id
        if submitter_name is None:
            if hasattr(user, 'full_name'):
                submitter_name = user.full_name
        elif (submitter_name
              and (getattr(user, 'full_name', None) != submitter_name)):
            # XXX We're being cavalier about stashing the full_name.
            user.full_name = submitter_name
        self.submitter_name = submitter_name

        if kibitzers is None:
            kibitzers = ()
        self.kibitzers = kibitzers

        self.topic = topic
        self.classification = classification
        self.security_related = (security_related and 1) or 0
        self.importance = importance
        self.severity = severity
        self.resolution = resolution
        self.reported_version = reported_version
        self.other_version_info = other_version_info

        self.portal_type = 'Collector Issue'
        container._setObject(id, self)
        # 'contained' is for stuff that needs collector acquisition wrapping.
        contained = container._getOb(id)
        contained._setPortalTypeName('Collector Issue')
        DefaultDublinCoreImpl.__init__(contained,
                                       title=title, description=description,
                                       effective_date=effective_date,
                                       expiration_date=expiration_date)

        if modification_date is None:
            modification_date = self.creation_date
        self.modification_date = modification_date

        contained.do_action('request', description, assignees,
                            file, fileid, filetype)

    def _set_collector_path(self, collector):
        """Stash path to containing collector."""
        # For getting the internal catalog when being indexed - at which 
        # time we don't have an acquisition content to use...
        self._collector_path = "/".join(collector.getPhysicalPath())

    security.declareProtected(CMFCorePermissions.View, 'CookedBody')
    def CookedBody(self):
        """Massage the transcript's cooked body to linkify obvious things."""
        return self._cook_links(self.get_transcript().CookedBody(stx_level=3))

    def _cook_links(self, text, email=0):
        """Cook text so URLs and upload references are hrefs.

        If optional arg 'email' is true, then we just provide urls for uploads
        (assuming the email client will take care of linkifying URLs)."""
        if not email:
            text = urlexp.sub(r'<a href=\1>\1</a>', text)
            text = uploadexp.sub(r'\1<a href="%s/\2/view">\2</a>\3'
                                 % self.absolute_url(),
                                 text)
        else:
            text = uploadexp.sub(r'\1 "\2" - %s/\2/view'
                                 % self.absolute_url(),
                                 text)
            text = string.replace(text, "<hr>", "-" * 62)
        return text
        

    security.declareProtected(EditCollectorIssue, 'edit')
    def edit(self,
             title=None,
             security_related=None,
             description=None,
             topic=None,
             classification=None,
             importance=None,
             severity=None,
             reported_version=None,
             other_version_info=None,
             text=None):
        """Update the explicitly passed fields."""

        changes = []
        changed = self._changed

        transcript = self.get_transcript()
        text = text.replace('\r', '')
        if text is not None and text != transcript.text:
            changes.append('revised transcript')
            transcript._edit(text_format=DEFAULT_TRANSCRIPT_FORMAT,
                             text=text)
        if changed('title', title):
            changes.append('revised title')
            self.title = title
        if ((security_related is not None)
            and ((not security_related) != (not self.security_related))):
            changes.append('security_related %s'
                           % (security_related and 'set' or 'unset'))
            self.security_related = (security_related and 1) or 0
        if changed('description', description):
            changes.append('revised description')
            self.description = description
        if changed('topic', topic):
            changes.append('topic (%s => %s)' % (self.topic, topic))
            self.topic = topic
        if changed('importance', importance):
            changes.append('importance (%s => %s)'
                           % (self.importance, importance))
            self.importance = importance
        if changed('classification', classification):
            changes.append('classification (%s => %s)'
                           % (self.classification, classification))
            self.classification = classification
        if changed('severity', severity):
            changes.append('severity (%s => %s)'
                           % (self.severity, severity))
            self.severity = severity
        if changed('reported_version', reported_version):
            changes.append('reported_version (%s => %s)'
                           % (self.reported_version, reported_version))
            self.reported_version = reported_version
        if changed('other_version_info', other_version_info):
            changes.append('revised other_version_info')
            self.other_version_info = other_version_info

        if not changes:
            return 'No changes.'

        self.action_number += 1

        username = str(getSecurityManager().getUser())

        transcript._edit('stx',
                         self._entry_header('Edit', username)
                         + "\n\n"
                         + " Changes: " + ", ".join(changes)
                         + ((self.action_number > 1) and "\n\n<hr>\n")
                         + transcript.EditableBody())
        self.reindexObject()
        self._send_update_notice('Edit', username)
        return ", ".join(changes)

    def _changed(self, field_name, value):
        """True if value is not None and different than self.field_name."""
        return ((value is not None) and
                (getattr(self, field_name, None) != value))

    security.declareProtected(CMFCorePermissions.View, 'get_transcript')
    def get_transcript(self):
        return self._getOb(TRANSCRIPT_NAME)
    
    security.declareProtected(AddCollectorIssueFollowup, 'do_action')
    def do_action(self, action, comment,
                  assignees=None, file=None, fileid=None, filetype=None):
        """Execute an action, adding comment to the transcript."""

        action_number = self.action_number = self.action_number + 1
        username = str(getSecurityManager().getUser())

        orig_supporters = self.assigned_to()
        # Strip off '_confidential' from status, if any.
        orig_status = string.split(self.status(), '_')[0]

        if string.lower(action) != 'comment':
            # Confirm against portal actions tool:
            if action != 'request' and action not in self._valid_actions():
                raise 'Unauthorized', "Invalid action '%s'" % action

            self.portal_workflow.doActionFor(self,
                                             action,
                                             comment=comment,
                                             username=username,
                                             assignees=assignees)

        new_status = string.split(self.status(), '_')[0]

        if string.lower(action) == 'request':
            self._create_transcript(comment)
        transcript = self.get_transcript()

        comment_header = [self._entry_header(action, username)]

        if (orig_status
            and (orig_status != 'New')
            and (new_status != orig_status)):
            comment_header.append(" Status: %s => %s"
                                  % (orig_status, new_status))

        additions, removals = self._supporters_diff(orig_supporters)
        if additions or removals:
            if additions:
                reroster = " Supporters added: %s" % ", ".join(additions)
                if removals:
                    reroster += "; removed: %s" % ", ".join(removals)
            elif removals:
                reroster = " Supporters removed: %s" % ", ".join(removals)
            comment_header.append(reroster)

        (uploadmsg, fileid) = self._process_file(file, fileid,
                                                  filetype, comment)
        if uploadmsg:
            comment_header.append(" " + uploadmsg)

        comment_header_str = "\n\n".join(comment_header) + "\n\n"

        transcript._edit('stx',
                         comment_header_str
                         + util.process_comment(string.strip(comment))
                         + ((action_number > 1) and "\n<hr>\n" or '')
                         + transcript.EditableBody())
        self.reindexObject()
        self._send_update_notice(action, username,
                                 orig_status, additions, removals,
                                 file=file, fileid=fileid)

    def _supporters_diff(self, orig_supporters):
        """Indicate supporter roster changes, relative to orig_supporters.

        Return (list-of-added-supporters, list-of-removed-supporters)."""
        plus, minus = list(self.assigned_to()), []
        for supporter in orig_supporters:
            if supporter in plus: plus.remove(supporter)
            else: minus.append(supporter)
        return (plus, minus)

    def _send_update_notice(self, action, actor,
                            orig_status=None, additions=None, removals=None,
                            file=None, fileid=None):
        """Send email notification about issue event to relevant parties."""

        action = string.capitalize(string.split(action, '_')[0])
        new_status = string.split(self.status(), '_')[0]

        recipients = []
        didids = []; gotemails = []     # Duplicate prevention.

        # Who to notify:
        # We want to noodge only assigned supporters while it's being worked
        # on, ie assigned supporters are corresponding about it, otherwise
        # everyone gets updates:
        # - Requester always
        # - All supporters:
        #   - When an issue is any state besides accepted
        #   - When an issue is being accepted
        #   - When an issue is accepted and moving to another state
        # - Relevant supporters when an issue is accepted:
        #   - those supporters assigned to the issue
        #   - any supporters being removed from or added to an issue.
        candidates = [self.submitter_id]
        if orig_status and not ('accepted' == string.lower(new_status) == 
                                string.lower(orig_status)):
            candidates.extend(self.aq_parent.supporters)
        else:
            candidates.extend(self.assigned_to())
            if removals:
                # Notify supporters being removed from the issue (confirms 
                # their action, if they're resigning, and informs them if
                # manager is deassigning them).
                candidates.extend(removals)

        for userid in candidates:
            if userid in didids:
                continue
            didids.append(userid)
            name, email = util.get_email_fullname(self, userid)
            if email:
                if email in gotemails:
                    continue
                gotemails.append(email)
                recipients.append((name, email))

        if recipients:
            to = ", ".join(["%s <%s>" % (name, email)
                            for name, email in recipients])
            title = self.aq_parent.title[:50]
            short_title = " ".join(title[:40].split(" ")[:-1]) or title
            if short_title != title[:40]:
                short_title = short_title + " ..."
            sender = ('"Collector: %s" <%s>'
                      % (short_title, self.aq_parent.email))

            if '.' in title or ',' in title:
                title = '"%s"' % title

            if self.abbrev:
                subject = "[%s]" % self.abbrev
            else: subject = "[Collector]"
            subject = ('%s %s/%2d %s "%s"'
                       % (subject, self.id, self.action_number,
                          string.capitalize(action), self.title))

            body = self._cook_links(self.get_transcript().text, email=1)
            cin = self.collector_issue_notice
            message = cin(sender=sender,
                          recipients=to,
                          subject=subject,
                          issue_id=self.id,
                          action=action,
                          actor=actor,
                          number=self.action_number,
                          security_related=self.security_related,
                          confidential=self.confidential(),
                          title=self.title,
                          submitter_name=self.submitter_name,
                          status=new_status,
                          klass=self.classification,
                          topic=self.topic,
                          importance=self.importance,
                          severity=self.severity,
                          issue_url=self.absolute_url(),
                          body=body,
                          candidates=candidates)
            mh = self.MailHost
            mh.send(message)

    def _process_file(self, file, fileid, filetype, comment):
        """Upload file to issue if it is substantial (has a name).

        Return a message describing the file, for transcript inclusion."""
        if file and file.filename:
            if not fileid:
                fileid = string.split(string.split(file.filename, '/')[-1],
                                      '\\')[-1]
            upload = self._add_artifact(fileid, filetype, comment, file)
            uploadmsg = "%s%s" % (UPLOAD_PREFIX, fileid)
            return (uploadmsg, fileid)
        else:
            return ('', '')

    def _add_artifact(self, id, type, description, file):
        """Add new artifact, and return object."""
        self.invokeFactory(type, id)
        it = self._getOb(id)
        # Acquire view and access permissions from container
        it.manage_permission('View', acquire=1)
        it.manage_permission('Access contents information', acquire=1)
        it.description = description
        it.manage_upload(file)
        return it

    def upload_number(self):
        """ """
        return len(self)

    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self):
        """Return the current supporters list, according to workflow."""
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'assigned_to', ()) or ()

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """True iff the current user is among .assigned_to()."""
        username = str(getSecurityManager().getUser())
        return username in (self.assigned_to() or ())

    security.declareProtected(CMFCorePermissions.View, 'status')
    def status(self):
        """Return the current status according to workflow."""
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'state', 'Pending')

    security.declareProtected(CMFCorePermissions.View, 'review_state')
    review_state = status

    security.declareProtected(CMFCorePermissions.View, 'confidential')
    def confidential(self):
        """True if workflow has the issue marked confidential.

        (Security_related issues start confidential, and are made
        unconfidential on any completion.)"""
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'confidential', 0)

    def _create_transcript(self, description,
                           text_format=DEFAULT_TRANSCRIPT_FORMAT):
        """Create events and comments transcript, with initial entry."""

        user = getSecurityManager().getUser()
        addDocument(self, TRANSCRIPT_NAME, description=description)
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')
        it.title = self.title

    def _entry_header(self, type, user, prefix="= ", suffix=""):
        """Return text for the header of a new transcript entry."""
        # Ideally this would be a skin method (probly python script), but i
        # don't know how to call it from the product, sigh.
        t = string.capitalize(type)
        if self.action_number:
            lead = t + " - Entry #" + str(self.action_number)
        else:
            lead = t

        return ("%s%s by %s on %s%s" %
                (prefix, lead, str(user), DateTime().aCommon(), suffix))

    security.declareProtected(CMFCorePermissions.View, 'cited_text')
    def cited_text(self):
        """Quote text for use in literal citations."""
        return util.cited_text(self.get_transcript().text)

    def _valid_actions(self):
        """Return actions valid according to workflow and application logic."""

        pa = getToolByName(self, 'portal_actions', None)
        allactions = pa.listFilteredActionsFor(self)
        return [entry['name']
                for entry in allactions.get('issue_workflow', [])]

    security.declareProtected(CMFCorePermissions.View, 'valid_actions_pairs')
    def valid_actions_pairs(self):
        """Return ordered (prettyname, rawname) valid workflow action names."""
        # XXX I would do this with a python script method, but i'm hitting
        #     inability to assign to indexes (eg, 'list[x] = 1' or 
        #     'dict[x] = 1'), so having to resort to python code, sigh.

        order=self.ACTIONS_ORDER
        got = [()] * len(order)
        remainder = []

        for raw in self._valid_actions():
            pretty = raw.split('_')[0].capitalize()
            if pretty in order:
                got[order.index(pretty)] = (raw, pretty)
            else:
                remainder.append((raw, pretty))
        return filter(None, got) + remainder


    #################################################
    # Dublin Core and search provisions

    # The transcript indexes itself, we just need to index the salient
    # attribute-style issue data/metadata...

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'indexObject')
    def indexObject(self):
        for i in (self._get_internal_catalog(),
                  getToolByName(self, 'portal_catalog', None)):
            if i is not None:
                i.indexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'unindexObject')
    def unindexObject(self):
        for i in (self._get_internal_catalog(),
                  getToolByName(self, 'portal_catalog', None)):
            if i is not None:
                i.unindexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'reindexObject')
    def reindexObject(self, internal_only=0):
        catalogs = [self._get_internal_catalog()]
        if not internal_only:
            catalogs.append(getToolByName(self, 'portal_catalog', None))
        for i in catalogs:
            if i is not None:
                i.reindexObject(self)

    def _get_internal_catalog(self):
        if self._collector_path is None:
            # Last ditch effort - this will only work when we're being called
            # from the collector's .reindex_issues() method.
            self._set_collector_path(self.aq_parent)
        container = self.restrictedTraverse(self._collector_path)
        return container.get_internal_catalog()

    def manage_afterAdd(self, item, container):
        """Add self to the workflow and catalog."""
        # Are we being added (or moved)?
        if aq_base(container) is not aq_base(self):
            self._set_collector_path(self.aq_parent)
            wf = getToolByName(self, 'portal_workflow', None)
            if wf is not None:
                wf.notifyCreated(self)
            self.indexObject()

    def manage_beforeDelete(self, item, container):
        """Remove self from the catalog."""
        # Are we going away?
        if aq_base(container) is not aq_base(self):
            self.unindexObject()
            # Now let our "aspects" know we are going away.
            for it, subitem in self.objectItems():
                si_m_bD = getattr(subitem, 'manage_beforeDelete', None)
                if si_m_bD is not None:
                    si_m_bD(item, container)

    def SearchableText(self):
        """Consolidate all text and structured fields for catalog search."""
        # Make this a composite of the text and structured fields.
        return (self.title + ' '
                + self.description + ' '
                + self.topic + ' '
                + self.classification + ' '
                + self.importance + ' '
                + self.severity + ' '
                + self.status() + ' '
                + (self.resolution or '') + ' '
                + self.reported_version + ' '
                + self.other_version_info + ' '
                + ((self.security_related and 'security_related') or ''))

    def Subject(self):
        """The structured attributes."""
        return (self.topic,
                self.classification,
                self.importance,
                self.severity,
                )

    def __len__(self):
        """Number of uploaded artifacts (ie, excluding transcript)."""
        return len(self.objectIds()) - 1

    def __repr__(self):
        return ("<%s %s \"%s\" at 0x%s>"
                % (self.__class__.__name__,
                   self.id, self.title,
                   hex(id(self))[2:]))

InitializeClass(CollectorIssue)
    

def addCollectorIssue(self,
                      id,
                      title='',
                      description='',
                      submitter_id=None,
                      submitter_name=None,
                      kibitzers=None,
                      topic=None,
                      classification=None,
                      security_related=0,
                      importance=None,
                      severity=None,
                      reported_version=None,
                      other_version_info=None,
                      assignees=None,
                      file=None, fileid=None, filetype=None,
                      REQUEST=None):
    """
    Create a new issue in the collector.
    """

    it = CollectorIssue(id=id,
                        container=self,
                        title=title,
                        description=description,
                        submitter_id=submitter_id,
                        submitter_name=submitter_name,
                        kibitzers=kibitzers,
                        topic=topic,
                        classification=classification,
                        security_related=security_related,
                        importance=importance,
                        severity=severity,
                        reported_version=reported_version,
                        other_version_info=other_version_info,
                        assignees=assignees,
                        file=file, fileid=fileid, filetype=filetype)
    return id
