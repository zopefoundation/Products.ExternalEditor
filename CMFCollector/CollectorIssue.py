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

DEFAULT_TRANSCRIPT_FORMAT = 'stx'

factory_type_information = (
    {'id': 'Collector Issue',
#XXX     'content_icon': 'event_icon.gif',
     'meta_type': 'CMF Collector Issue',
     'description': ('A Collector Issue represents a bug report or'
                     ' other support request.'),
     'product': 'CMFCollector',
     'factory': None,                   # So not included in 'New' add form
     'allowed_content_types': ('Collector Issue Transcript', 'File', 'Image'), 
     'immediate_view': 'collector_edit_form',
     'actions': ({'id': 'view',
                  'name': 'Transcript',
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

    comment_number = 1

    ACTIONS_ORDER = ['Accept', 'Resign', 'Assign',
                     'Resolve', 'Reject', 'Defer'] 

    def __init__(self, 
                 id, container,
                 title='', description='',
                 submitter_id=None, submitter_name=None, submitter_email=None,
                 kibitzers=None,
                 topic=None, classification=None,
                 security_related=0,
                 importance=None, severity=None,
                 resolution=None,
                 reported_version=None, other_version_info=None,
                 creation_date=None, modification_date=None,
                 effective_date=None, expiration_date=None):
        """ """

        SkinnedFolder.__init__(self, id, title)
        # Take care of standard metadata:
        DefaultDublinCoreImpl.__init__(self,
                                       title=title, description=description,
                                       effective_date=effective_date,
                                       expiration_date=expiration_date)
        if modification_date is None:
            modification_date = self.creation_date
        self.modification_date = modification_date

        self._create_transcript(description, container)

        user = getSecurityManager().getUser()
        if submitter_id is None:
            self.submitter_id = str(user)
        self.submitter_id = submitter_id
        if submitter_name is None:
            if hasattr(user, 'full_name'):
                submitter_name = user.full_name
        elif (submitter_name
              and (getattr(user, 'full_name', None) != submitter_name)):
            # XXX We're being cavalier about stashing the full_name.
            user.full_name = submitter_name
        self.submitter_name = submitter_name
        if submitter_email is None and hasattr(user, 'email'):
            submitter_email = user.email
        self.submitter_email = submitter_email

        if kibitzers is None:
            kibitzers = ()
        self.kibitzers = kibitzers

        self.topic = topic
        self.classification = classification
        self.security_related = security_related
        self.importance = importance
        self.severity = severity
        self.resolution = resolution
        self.reported_version = reported_version
        self.other_version_info = other_version_info

        self.edited = 0

        return self

    security.declareProtected(EditCollectorIssue, 'edit')
    def edit(self, comment=None,
             text=None,
             status=None,
             submitter_name=None,
             title=None,
             description=None,
             security_related=None,
             topic=None,
             importance=None,
             classification=None,
             severity=None,
             reported_version=None,
             other_version_info=None):
        """Update the explicitly passed fields."""
        if text is not None:
            transcript = self.get_transcript()
            transcript._edit(text_format=DEFAULT_TRANSCRIPT_FORMAT,
                             text=text)
        if comment is not None:
            self.do_action('edit', comment)
        if submitter_name is not None:
            self.submitter_name = submitter_name
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if security_related is not None:
            self.security_related = security_related
        if topic is not None:
            self.topic = topic
        if importance is not None:
            self.importance = importance
        if classification is not None:
            self.classification = classification
        if severity is not None:
            self.severity = severity
        if reported_version is not None:
            self.reported_version = reported_version
        if other_version_info is not None:
            self.other_version_info = other_version_info
        self.edited = 1

    security.declareProtected(CMFCorePermissions.View, 'get_transcript')
    def get_transcript(self):
        return self._getOb(TRANSCRIPT_NAME)
    
    security.declareProtected(AddCollectorIssueFollowup, 'do_action')
    def do_action(self, action, comment,
                  assignees=None, file=None, fileid=None, filetype=None):
        """Execute an action, adding comment to the transcript."""

        username = str(getSecurityManager().getUser())

        if string.lower(action) != 'comment':
            # Confirm against portal actions tool:
            if action not in self._valid_actions():
                raise 'Unauthorized', "Invalid action '%s'" % action

            self.portal_workflow.doActionFor(self,
                                             action,
                                             comment=comment,
                                             username=username,
                                             assignees=assignees)

        if file is not None:
            if not fileid:
                fileid = string.split(string.split(file.filename, '/')[-1],
                                      '\\')[-1]
            attachment = self._add_artifact(fileid, filetype, comment, file)
            attachment_msg = (" - Attachment: %s\n\n" % fileid)
        else:
            attachment_msg = ''

        transcript = self.get_transcript()
        self.comment_number = self.comment_number + 1
        entry_leader = self._entry_header(action, username) + "\n\n"
        transcript._edit('stx',
                         entry_leader
                         + attachment_msg
                         + util.process_comment(string.strip(comment))
                         + "\n<hr>\n"
                         + transcript.EditableBody())

    def _add_artifact(self, id, type, description, file):
        """Add new artifact, and return object."""
        self.invokeFactory(type, id)
        it = self._getOb(id)
        it.description = description
        it.manage_upload(file)
        return it

    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self):
        """Return the current supporters list, according to workflow."""
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'assigned_to', [])

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """True iff the current user is among .assigned_to()."""
        username = str(getSecurityManager().getUser())
        return username in self.assigned_to()

    security.declareProtected(CMFCorePermissions.View, 'status')
    def status(self):
        """Return the current status according to workflow."""
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'state', '??')

    def _create_transcript(self, description, container,
                           text_format=DEFAULT_TRANSCRIPT_FORMAT):
        """Create events and comments transcript, with initial entry."""

        user = getSecurityManager().getUser()
        addDocument(self, TRANSCRIPT_NAME, description=description)
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')
        text = ("%s\n\n %s " %
                (self._entry_header('Request', user, prefix="== "),
                 description))
        it._edit(text_format=text_format, text=text)
        it.title = self.title

    def _entry_header(self, type, user, prefix=" == ", suffix=" =="):
        """Return text for the header of a new transcript entry."""
        # Ideally this would be a skin method (probly python script), but i
        # don't know how to call it from the product, sigh.
        t = string.capitalize(type)
        if self.comment_number:
            lead = t + " - Entry #" + str(self.comment_number)
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
        return [entry['name']
                for entry in pa.listFilteredActionsFor(self)['issue_workflow']]

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
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.indexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'unindexObject')
    def unindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.unindexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'reindexObject')
    def reindexObject(self):
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self)

    def manage_afterAdd(self, item, container):
        """Add self to the workflow and catalog."""
        # Are we being added (or moved)?
        if aq_base(container) is not aq_base(self):
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
                + self.resolution + ' '
                + self.reported_version + ' '
                + self.other_version_info + ' '
                + ((self.security_related and 'security_related') or ''))

    def Subject(self):
        """The structured attrs, combined w/field names for targeted search."""
        assigned_to = tuple(['assigned_to:' + i for i in self.assigned_to()])
        return ('topic:' + self.topic,
                'classification:' + self.classification,
                'security_related:' + ((self.security_related and '1') or '0'),
                'importance:' + self.importance,
                'severity:' + self.severity,
                'status:' + (self.status() or ''),
                'resolution:' + (self.resolution or ''),
                'reported_version:' + self.reported_version) + assigned_to

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
                      submitter_email=None,
                      kibitzers=None,
                      topic=None,
                      classification=None,
                      security_related=0,
                      importance=None,
                      severity=None,
                      reported_version=None,
                      other_version_info=None,
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
                        submitter_email=submitter_email,
                        kibitzers=kibitzers,
                        topic=topic,
                        classification=classification,
                        security_related=security_related,
                        importance=importance,
                        severity=severity,
                        reported_version=reported_version,
                        other_version_info=other_version_info)
    it._setPortalTypeName('Collector Issue')
    self._setObject(id, it)
    return id
