##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Implement the Collector Issue content type - a bundle containing the
collector transcript and various parts."""

import os, urllib, string, re
import smtplib

from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base

import util                             # Collector utilities.

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from WebTextDocument import addWebTextDocument

# Import permission names
from Products.CMFCore import CMFCorePermissions
from CollectorPermissions import *

RULE = '_' * 40

UPLOAD_PREFIX = "Uploaded: "
uploadexp = re.compile('(%s)([^<,\n]*)([<,\n])'
                       % UPLOAD_PREFIX, re.MULTILINE)

factory_type_information = (
    {'id': 'Collector Issue',
     'icon': 'collector_issue_icon.gif',
     'meta_type': 'CMF Collector Issue',
     'description': ('A Collector Issue represents a bug report or'
                     ' other support request.'),
     'product': 'CMFCollector',
     'factory': None,                   # So not included in 'New' add form
     'allowed_content_types': ('Collector Issue Transcript',
                               'File', 'Image'), 
     'immediate_view': 'collector_edit_form',
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'collector_issue_contents',
                  'permissions': (ViewCollector,)},
                 {'id': 'followup',
                  'name': 'Followup',
                  'action': 'collector_issue_followup_form',
                  'permissions': (AddCollectorIssueFollowup,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'collector_issue_edit_form',
                  'permissions': (EditCollectorIssue,)},
                 {'id': 'browse',
                  'name': 'Browse',
                  'action': 'collector_issue_up',
                  'permissions': (ViewCollector,)},
                 {'id': 'addIssue',
                  'name': 'New',
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
    TRANSCRIPT_FORMAT = 'webtext'
    
    security = ClassSecurityInfo()

    action_number = 0

    ACTIONS_ORDER = ['Accept', 'Assign',
                     'Resolve', 'Reject', 'Defer',
                     'Resign'] 

    # Accumulated instance-data backwards-compatability values:
    _collector_path = None
    # XXX This security declaration doesn't seem to have an effect?
    security.declareProtected(EditCollectorIssue, 'submitter_email')
    submitter_email = None
    submitter_name = None
    invisible = 0
    version_info = ''

    def __init__(self,
                 id, container, 
                 title='', description='',
                 submitter_id=None, submitter_name=None,
                 submitter_email=None,
                 kibitzers=None,
                 security_related=0,
                 topic=None, classification=None, importance=None, 
                 resolution=None,
                 version_info=None,
                 creation_date=None, modification_date=None,
                 effective_date=None, expiration_date=None,
                 assignees=None,
                 file=None, fileid=None, filetype=None,
                 invisible=0):
        """ """

        self.invisible = invisible
        SkinnedFolder.__init__(self, id, title)
        self._set_collector_path(container)

        mbtool = getToolByName(container, 'portal_membership')
        user = mbtool.getAuthenticatedMember()
        if submitter_id is None:
            submitter_id = str(user)
        self.submitter_id = submitter_id
        self.__of__(container)._set_submitter_specs(submitter_id,
                                                    submitter_name,
                                                    submitter_email)

        if kibitzers is None:
            kibitzers = ()
        self.kibitzers = kibitzers

        self.topic = topic
        self.classification = classification
        self.security_related = (security_related and 1) or 0
        self.importance = importance
        self.resolution = resolution
        self.version_info = version_info

        self.portal_type = 'Collector Issue'
        # 'contained' is for stuff that needs collector acquisition wrapping.
        container._setObject(id, self)
        contained = container._getOb(id)
        contained._setPortalTypeName('Collector Issue')
        DefaultDublinCoreImpl.__init__(contained,
                                       title=title, description=description,
                                       effective_date=effective_date,
                                       expiration_date=expiration_date)

        if modification_date is None:
            modification_date = self.creation_date
        self.modification_date = modification_date

    def _set_submitter_specs(self, submitter_id,
                             submitter_name, submitter_email):
        """Given an id, set the name and email as warranted."""

        mbrtool = getToolByName(self, 'portal_membership')
        user = mbrtool.getMemberById(submitter_id)
        changes = []
        if self.submitter_id != submitter_id:
            if user is None:
                if ((string.lower(submitter_id[:len('anonymous')])
                     == 'anonymous')
                    or not submitter_id):
                    user = self.acl_users._nobody
                    submitter_id = str(user)
                else:
                    raise ValueError, "User '%s' not found" % submitter_id
            changes.append("Submitter id: '%s' => '%s'" % (self.submitter_id,
                                                           submitter_id))
            self.submitter_id = submitter_id

        if not submitter_name:
            name = util.safeGetProperty(user, 'full_name', '')
            if name: submitter_name = name
            else: submitter_name = submitter_id
        if self.submitter_name != submitter_name:
            changes.append('submitter name')
            self.submitter_name = submitter_name
        email_pref = util.safeGetProperty(user, 'email', '')
        if submitter_email and submitter_email == email_pref:
            # A bit different than you'd expect: only stash the specified
            # email if it's different than the member-preference.  Otherwise,
            # stash None, so the preference is tracked at send time.
            submitter_email = None
        if self.submitter_email != submitter_email:
            changes.append("submitter email")
            self.submitter_email = submitter_email
        return changes

    def _set_collector_path(self, collector):
        """Stash path to containing collector."""
        # For getting the internal catalog when being indexed - at which 
        # time we may not have an acquisition context...
        self._collector_path = "/".join(collector.getPhysicalPath())

    security.declareProtected(CMFCorePermissions.View, 'no_submitter_email')
    def no_submitter_email(self):
        """True if there's no way to get email address for the submitter."""
        if self.submitter_email:
            return 0
        if self.submitter_id != str(self.acl_users._nobody):
            member = self.portal_membership.getMemberById(self.submitter_id)
            if member:
                email_pref = util.safeGetProperty(member, 'email', '')
                return not email_pref
        return 1

    security.declareProtected(CMFCorePermissions.View, 'CookedBody')
    def CookedBody(self):
        """Rendered content."""
        body = self.get_transcript().CookedBody()
        return uploadexp.sub(r'\1 <a href="%s/\2/view">\2</a>\3'
                             % self.absolute_url(),
                             body)


    security.declareProtected(EditCollectorIssue, 'edit')
    def edit(self,
             title=None,
             submitter_id=None, submitter_name=None, submitter_email=None,
             security_related=None,
             description=None,
             topic=None,
             classification=None,
             importance=None,
             version_info=None,
             stealthy=None,
             comment=None,
             text=None):
        """Update the explicitly passed fields."""

<<<<<<< CollectorIssue.py
<<<<<<< CollectorIssue.py
    ACTIONS_ORDER = [ 'Accept'
                    , 'Assign'
                    , 'Resolve'
                    , 'Reject'
                    , 'Defer'
                    , 'Resign'
                    ] 

    _action_number = 0

    _submitter_id = _submitter_email = _submitter_name = None
    _supporters = ()
    _kibitzers = ()
    _security_related = 0
    _topic = _classification = _importance = _resolution = None
    _version_info = ''
    _invisible = 0

    def __init__( self
                , id
                , title=''
                , description=''
                ):

        SkinnedFolder.__init__( self
                              , id
                              , title
                              )

        DefaultDublinCoreImpl.__init__( self
                                      , title=title
                                      , description=description
                                      )

        self._create_transcript( title, description )

    #
    #   Property management.
    #
    security.declareProtected( CMFCorePermissions.View, 'isSecurityRelated' )
    def isSecurityRelated( self ):
        """
            Is this issue related to security (and therefore, should it
            receive special handling)?
        """
        return self._security_related

    security.declareProtected( EditCollectorIssue, 'setSecurityRelated' )
    def setSecurityRelated( self, security_related ):
        """
            Assign the "security related" flag.
        """
        self._security_related = not not security_related

    security.declareProtected( CMFCorePermissions.View, 'getTopic' )
    def getTopic( self ):
        """
            What is the "topic" of this issue (typically, the
            subsystem, package, or component to which it pertains)?
        """
        return self._topic

    security.declareProtected( EditCollectorIssue, 'setTopic' )
    def setTopic( self, topic ):
        """
            Assign the "topic" field.
        """
        self._topic = topic

    security.declareProtected( CMFCorePermissions.View, 'getClassification' )
    def getClassification( self ):
        """
            What is the "kind" of this issue (typically, bug report,
            feature request, etc.)?
        """
        return self._classification

    security.declareProtected( EditCollectorIssue, 'setClassification' )
    def setClassification( self, classification ):
        """
            Assign the "classification" field.
        """
        self._classification = classification

    security.declareProtected( CMFCorePermissions.View, 'getImportance' )
    def getImportance( self ):
        """
            What is the "importance" of this issue (typically, "critical",
            "high", etc.)?
        """
        return self._importance

    security.declareProtected( EditCollectorIssue, 'setImportance' )
    def setImportance( self, importance ):
        """
            Assign the "importance" field.
        """
        self._importance = importance

    security.declareProtected( CMFCorePermissions.View, 'getVersionInfo' )
    def getVersionInfo( self ):
        """
            To what "version" of the software does the issue pertain?
        """
        return self._version_info

    security.declareProtected( EditCollectorIssue, 'setVersionInfo' )
    def setVersionInfo( self, version_info ):
        """
            Assign the "importance" field.
        """
        self._version_info = version_info

    security.declareProtected( CMFCorePermissions.View, 'isInvisible' )
    def isInvisible( self ):
        """
            Is this issue "hidden" from catalog queries?
        """
        return self._invisible

    security.declareProtected( EditCollectorIssue, 'setInvisible' )
    def setInvisible( self, invisible ):
        """
            Assign invisibility.
        """
        self._invisible = invisible

    security.declareProtected( EditCollectorIssue, 'edit' )
    def edit( self
            , title=None
            , description=None
            , security_related=None
            , topic=None
            , classification=None
            , importance=None
            , version_info=None
            , comment=None
            , text=None
            , submitter_id=None
            , submitter_name=None
            , submitter_email=None
            ):
        """
            Update the explicitly passed fields.
        """
=======
    ACTIONS_ORDER = [ 'Accept'
                    , 'Assign'
                    , 'Resolve'
                    , 'Reject'
                    , 'Defer'
                    , 'Resign'
                    ] 

    _action_number = 0

    _security_related = 0
    _topic = _classification = _importance = _resolution = None
    _version_info = ''
    _invisible = 0
    _submitter_id = _submitter_email = _submitter_name = None
    _supporters = ()
    _kibitzers = ()

    def __init__( self
                , id
                , title=''
                , description=''
                , creation_date=None
                , effective_date=None
                , expiration_date=None
                , submitter_id=None
                , submitter_name=None
                , submitter_email=None
                , supporters=None
                , kibitzers=None
                , security_related=0
                , topic=None
                , classification=None
                , importance=None
                , resolution=None
                , version_info=''
                , invisible=0
                ):

        SkinnedFolder.__init__( self
                              , id
                              , title
                              )

        DefaultDublinCoreImpl.__init__( self
                                      , title=title
                                      , description=description
                                      , effective_date=effective_date
                                      , expiration_date=expiration_date
                                      )
        if creation_date is not None:
            self.creation_date = creation_date

        self._submitter_id = submitter_id
        self._submitter_name = submitter_name
        self._submitter_email = submitter_email
        self._supporters = supporters or ()
        self._kibitzers = kibitzers or ()

        self.setSecurityRelated( security_related )
        self._topic = topic
        self._classification = classification
        self._importance = importance
        self._resolution = resolution
        self._version_info = version_info
        self._invisible = invisible

        self._create_transcript( description )

    #
    #   Property management.
    #
    security.declareProtected( CMFCorePermissions.View, 'isSecurityRelated' )
    def isSecurityRelated( self ):
        """
            Is this issue related to security (and therefore, should it
            receive special handling)?
        """
        return self._security_related

    security.declareProtected( EditCollectorIssue, 'setSecurityRelated' )
    def setSecurityRelated( self, security_related ):
        """
            Assign the "security related" flag.
        """
        self._security_related = not not security_related

    security.declareProtected( CMFCorePermissions.View, 'getTopic' )
    def getTopic( self ):
        """
            What is the "topic" of this issue (typically, the
            subsystem, package, or component to which it pertains)?
        """
        return self._topic

    security.declareProtected( EditCollectorIssue, 'setTopic' )
    def setTopic( self, topic ):
        """
            Assign the "topic" field.
        """
        self._topic = topic

    security.declareProtected( CMFCorePermissions.View, 'getClassification' )
    def getClassification( self ):
        """
            What is the "kind" of this issue (typically, bug report,
            feature request, etc.)?
        """
        return self._classification

    security.declareProtected( EditCollectorIssue, 'setClassification' )
    def setClassification( self, classification ):
        """
            Assign the "classification" field.
        """
        self._classification = classification

    security.declareProtected( CMFCorePermissions.View, 'getImportance' )
    def getImportance( self ):
        """
            What is the "importance" of this issue (typically, "critical",
            "high", etc.)?
        """
        return self._importance

    security.declareProtected( EditCollectorIssue, 'setImportance' )
    def setImportance( self, importance ):
        """
            Assign the "importance" field.
        """
        self._importance = importance

    security.declareProtected( CMFCorePermissions.View, 'getVersionInfo' )
    def getVersionInfo( self ):
        """
            To what "version" of the software does the issue pertain?
        """
        return self._version_info

    security.declareProtected( EditCollectorIssue, 'setVersionInfo' )
    def setVersionInfo( self, version_info ):
        """
            Assign the "importance" field.
        """
        self._version_info = version_info

    security.declareProtected( EditCollectorIssue, 'edit' )
    def edit( self
            , title=None
            , description=None
            , security_related=None
            , topic=None
            , classification=None
            , importance=None
            , version_info=None
            , comment=None
            , text=None
            , submitter_id=None
            , submitter_name=None
            , submitter_email=None
            ):
        """
            Update the explicitly passed fields.
        """
>>>>>>> 1.38.2.1
        changes = []

        if self.hasChanged( 'Title', title ):
            changes.append('revised title')
            self.setTitle( title )

        if self.hasChanged( 'Description', description ):
            changes.append('revised description')
            self.setDescription( description )

        if self.hasChanged( 'isSecurityRelated', security_related ):
            changes.append('security_related %s'
                        % (security_related and 'set' or 'unset'))
            self.setSecurityRelated( security_related )

        if self.hasChanged( 'getTopic', topic ):
            changes.append('topic (%s => %s)' % (self._topic, topic))
            self.setTopic( topic )

        if self.hasChanged( 'getClassification', classification ):
            changes.append('classification (%s => %s)'
                           % (self.classification, classification))
            self.setClassification( classification )

        if self.hasChanged( 'getImportance', importance ):
            changes.append('importance (%s => %s)'
                           % (self.importance, importance))
            self.setImportance( importance )

        if self.hasChanged( 'getVersionInfo', version_info ):
            changes.append('revised version_info')
            self._version_info = version_info

        if comment:
            changes.append('new comment')

        transcript = self.get_transcript()
        text = text.replace('\r', '')

        if self.hasChanged( 'EditableBody', text  ):
            changes.append('edited transcript')
            transcript.edit(text_format=self.TRANSCRIPT_FORMAT, text=text)

        changes.extend( self.setSubmitter( submitter_id
                                         , submitter_name
                                         , submitter_email
                                         ) )
        if not changes:
            return 'No changes.'

        self._incrementActionNumber()

        username = str(getSecurityManager().getUser())

        if comment:
            comment = "\n\n" + comment
        else:
            comment = ''

        transcript.edit(self.TRANSCRIPT_FORMAT,
                         self._entry_header('Edit', username)
                         + "\n\n"
                         + " Changes: " + ", ".join(changes)
                         + comment
                         + ((self.getActionNumber() > 1) and "\n" + RULE + "\n")
                         + transcript.EditableBody())
        self.reindexObject()
        self._send_update_notice('Edit', username)
        return ", ".join(changes)

<<<<<<< CollectorIssue.py
    security.declareProtected( EditCollectorIssue, 'hasChanged' )
    def hasChanged( self, field_name, value ):
        """
            True if value is not None and different than self.field_name.
        """
        if value is None:
            return 0

        method = getattr( self, field_name )
        return method() != value
    
    #
    #   Manage data about the submitter.
    #
    security.declareProtected( EditCollectorIssue, 'getSubmitterEmail' )
    def getSubmitter( self ):
        """
            Return the member object for the submitter, or None
        """
        member = None

        if self._submitter_id is not None:
            try:
                mtool = getToolByName( self, 'portal_membership' )
            except AttributeError:
                pass
            else:
                member = mtool.getMemberById( self._submitter_id )
        
        return member

    security.declareProtected( EditCollectorIssue, 'getSubmitterId' )
    def getSubmitterId( self ):
        """
            Return the id of the submitter (None for anonymous submission).
        """
        return self._submitter_id

    security.declareProtected( EditCollectorIssue, 'getSubmitterName' )
    def getSubmitterName( self ):
        """
            Return the name of the submitter (defaults to the ID).
        """
        if self._submitter_name is not None:
            return self._submitter_name

        member = self.getSubmitter()

        if member:
            return util.safeGetProperty( member, 'full_name', None )

        return self._submitter_id or 'Anonymous'

    security.declareProtected( EditCollectorIssue, 'getSubmitterEmail' )
    def getSubmitterEmail( self ):
        """
            Return the e-mail address of the submitter, if possible.
        """
        if self._submitter_email is not None:
            return self._submitter_email

        member = self.getSubmitter()

        if member:
            return util.safeGetProperty( member, 'email', None )

        return None

    security.declareProtected( EditCollectorIssue, 'setSubmitter' )
    def setSubmitter( self
                    , submitter_id=None
                    , submitter_name=None
                    , submitter_email=None
                    ):
        """
            Given an id, set the name and email as warranted.

            Return a list of strings indicating the fields which have
            been changed.
        """
        changes = []
        member = None

        if submitter_id is not None:
            try:
                mtool = getToolByName( self, 'portal_membership' )
            except AttributeError:
                pass
            else:
                member = mtool.getMemberById( submitter_id )

        if self._submitter_id != submitter_id:
            changes.append( "submitter id: '%s' => '%s'"
                          % (self._submitter_id, submitter_id ) )
            self._submitter_id = submitter_id

        if self._submitter_name != submitter_name:
            changes.append('submitter name')
            self._submitter_name = submitter_name

        email_pref = util.safeGetProperty( member, 'email', '' )

        if submitter_email and submitter_email == email_pref:
            # A bit different than you'd expect: only stash the specified
            # email if it's different than the member-preference.  Otherwise,
            # stash None, so the preference is tracked at send time.
            submitter_email = None

        if self._submitter_email != submitter_email:
            changes.append("submitter email")
            self._submitter_email = submitter_email

        return changes

    #
    #   Manage supporters.
    #
    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self):
        """
            Return the current supporters list, according to workflow.

            XXX:  Deprectaed; retained only to allow conversions from 
                  old-style issues which didn't manage their own supporters.
        """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'assigned_to', ()) or ()

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """
            Return boolean indicating whehter the current user is a supporter.
        """
        mtool = getToolByName( self, 'portal_membership' )
        member = mtool.getAuthenticatedMember()

        return member.getUserName() in self.listSupporters()

    security.declarePublic( 'diffUserLists' )
    def diffUserLists( self, old, new ):
        """
            Return (list-of-added-users, list-of-removed-users).
        """
        plus, minus = list( new ), []

        for userid in list( old ):

            if userid in plus:
                plus.remove( userid )
            else:
                minus.append( userid )

        return ( plus, minus )

    security.declareProtected( CMFCorePermissions.View, 'listSupporters' )
    def listSupporters( self ):
        """
            Return a list (possibly empty) of user IDs of supporters
            assigned to this issue.
        """
        return self._supporters

    security.declareProtected( EditCollectorIssue, 'addSupporter' )
    def addSupporter( self, supporter ):
        """
            Add 'supporter' to the list of users who are assigned to
            this issue.
        """
        if supporter in self._supporters:
            raise ValueError, 'Already assigned: %s' % supporter

        supporters = list( self._supporters )
        supporters.append( supporter )
        self._supporters = tuple( supporters )

    security.declareProtected( EditCollectorIssue, 'removeSupporter' )
    def removeSupporter( self, supporter ):
        """
            Remove 'supporter' from the list of users who are assigned to
            this issue.
        """
        if supporter not in self._supporters:
            raise ValueError, 'Not assigned: %s' % supporter

        supporters = list( self._supporters )
        supporters.remove( supporter )
        self._supporters = tuple( supporters )

    security.declareProtected( EditCollectorIssue, 'setSupporters' )
    def setSupporters( self, supporters ):
        """
            Update our list of supporters;  return a list of strings
            indicating the changes (additions, removals).
        """
        changes = []

        added, removed = self.diffUserLists( self._supporters, supporters )
        self._supporters = tuple( supporters )

        if added:
            changes.append( 'added supporters: %s' % ' '.join( added ) )

        if removed:
            changes.append( 'removed supporters: %s' % ' '.join( removed ) )

        return changes

    security.declareProtected( EditCollectorIssue, 'clearSupporters' )
    def clearSupporters( self ):
        """
            Remove all supporters from an issue.
        """
        del self._supporters


    #
    #   Manage other interested parties.
    #
    security.declareProtected( CMFCorePermissions.View, 'listKibitzers' )
    def listKibitzers( self ):
        """
            Return a list (possibly empty) of user IDs of non-supporters
            who have subscribed to this issue.
        """
        return self._kibitzers

    security.declareProtected( EditCollectorIssue, 'addKibitzer' )
    def addKibitzer( self, kibitzer ):
        """
            Add 'kibitzer' to the list of users who are subscribed to
            this issue.
        """
        if kibitzer in self._kibitzers:
            raise ValueError, 'Already subscribed: %s' % kibitzer

        kibitzers = list( self._kibitzers )
        kibitzers.append( kibitzer )
        self._kibitzers = tuple( kibitzers )

    security.declareProtected( EditCollectorIssue, 'removeKibitzer' )
    def removeKibitzer( self, kibitzer ):
        """
            Remove 'kibitzer' from the list of users who are subscribed to
            this issue.
        """
        if kibitzer not in self._kibitzers:
            raise ValueError, 'Not subscribed: %s' % kibitzer

        kibitzers = list( self._kibitzers )
        kibitzers.remove( kibitzer )
        self._kibitzers = tuple( kibitzers )

    security.declareProtected( EditCollectorIssue, 'setKibitzers' )
    def setKibitzers( self, kibitzers ):
        """
            Update our list of kibitzers;  return a list of strings
            indicating the changes (additions, removals).
        """
        changes = []

        added, removed = self.diffUserLists( self._kibitzers, kibitzers )
        self._kibitzers = tuple( kibitzers )

        if added:
            changes.append( 'added kibitzers: %s' % ' '.join( added ) )

        if removed:
            changes.append( 'removed kibitzers: %s' % ' '.join( removed ) )

        return changes

    security.declareProtected( EditCollectorIssue, 'clearKibitzers' )
    def clearKibitzers( self ):
        """
            Remove all kibitzers from an issue.
        """
        del self._kibitzers

    #
    #   Manage the transcript.
    #
    security.declarePrivate( '_create_transcript' )
    def _create_transcript(self, title, description):
        """
            Create events and comments transcript, with initial entry.
        """
        addWebTextDocument( self
                          , TRANSCRIPT_NAME
                          , title=title
                          , description=description
                          )
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')

    security.declareProtected( CMFCorePermissions.View, 'getTranscript' )
    def getTranscript( self ):
        """
            Return the transcript
        """
        return self._getOb( TRANSCRIPT_NAME )

    get_transcript = getTranscript

    security.declareProtected( CMFCorePermissions.View, 'CookedBody' )
    def CookedBody( self ):
        """
            Render the transcript.
        """
        body = self.get_transcript().CookedBody()
        return uploadexp.sub(r'\1 <a href="%s/\2/view">\2</a>\3'
                             % self.absolute_url(),
                             body)

    security.declareProtected(CMFCorePermissions.View, 'cited_text')
    def cited_text(self):
        """
            Quote text for use in literal citations.
        """
        return util.cited_text( self.get_transcript().EditableBody() )
        
    #
    #   "Audit trail" management.
    #
    security.declarePrivate( '_incrementActionNumber')
    def _incrementActionNumber( self ):
        """
            Bump the "action" counter.
        """
        self._action_number += 1

    security.declareProtected( CMFCorePermissions.View, 'getActionNumber' )
    def getActionNumber( self ):
        """
            Return the sequence number of the most recent action.
        """
        return self._action_number
=======
    security.declareProtected( EditCollectorIssue, 'hasChanged' )
    def hasChanged( self, field_name, value ):
        """
            True if value is not None and different than self.field_name.
        """
        if value is None:
            return 0

        method = getattr( self, field_name )
        return method() != value
>>>>>>> 1.38.2.1
    
<<<<<<< CollectorIssue.py
    security.declareProtected( AddCollectorIssueFollowup, 'do_action')
    def do_action(self,
                  action,
                  comment,
                  file=None,
                  fileid=None,
                  filetype=None):
=======
    #
    #   Manage data about the submitter.
    #
    security.declareProtected( EditCollectorIssue, 'getSubmitterEmail' )
    def getSubmitter( self ):
        """
            Return the member object for the submitter, or None
        """
        member = None

        if self._submitter_id is not None:
            try:
                mtool = getToolByName( self, 'portal_membership' )
            except AttributeError:
                pass
            else:
                member = mtool.getMemberById( self._submitter_id )
        
        return member

    security.declareProtected( EditCollectorIssue, 'getSubmitterId' )
    def getSubmitterId( self ):
        """
            Return the id of the submitter (None for anonymous submission).
        """
        return self._submitter_id

    security.declareProtected( EditCollectorIssue, 'getSubmitterName' )
    def getSubmitterName( self ):
        """
            Return the name of the submitter (defaults to the ID).
        """
        if self._submitter_name is not None:
            return self._submitter_name

        member = self.getSubmitter()

        if member:
            return util.safeGetProperty( member, 'full_name', None )

        return self._submitter_id or 'Anonymous'

    security.declareProtected( EditCollectorIssue, 'getSubmitterEmail' )
    def getSubmitterEmail( self ):
        """
            Return the e-mail address of the submitter, if possible.
        """
        if self._submitter_email is not None:
            return self._submitter_email

        member = self.getSubmitter()

        if member:
            return util.safeGetProperty( member, 'email', None )

        return None

    security.declareProtected( EditCollectorIssue, 'setSubmitter' )
    def setSubmitter( self
                    , submitter_id=None
                    , submitter_name=None
                    , submitter_email=None
                    ):
        """
            Given an id, set the name and email as warranted.

            Return a list of strings indicating the fields which have
            been changed.
        """
        changes = []
        member = None

        if submitter_id is not None:
            try:
                mtool = getToolByName( self, 'portal_membership' )
            except AttributeError:
                pass
            else:
                member = mtool.getMemberById( submitter_id )

        if self._submitter_id != submitter_id:
            changes.append( "submitter id: '%s' => '%s'"
                          % (self._submitter_id, submitter_id ) )
            self._submitter_id = submitter_id

        if self._submitter_name != submitter_name:
            changes.append('submitter name')
            self._submitter_name = submitter_name

        email_pref = util.safeGetProperty( member, 'email', '' )

        if submitter_email and submitter_email == email_pref:
            # A bit different than you'd expect: only stash the specified
            # email if it's different than the member-preference.  Otherwise,
            # stash None, so the preference is tracked at send time.
            submitter_email = None

        if self._submitter_email != submitter_email:
            changes.append("submitter email")
            self._submitter_email = submitter_email

        return changes

    #
    #   Manage supporters.
    #
    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self):
        """
            Return the current supporters list, according to workflow.

            XXX:  Deprectaed; retained only to allow conversions from 
                  old-style issues which didn't manage their own supporters.
        """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'assigned_to', ()) or ()

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """
            Return boolean indicating whehter the current user is a supporter.
        """
        mtool = getToolByName( self, 'portal_membership' )
        member = mtool.getAuthenticatedMember()

        return member.getUserName() in self.listSupporters()

    security.declarePublic( 'diffUserLists' )
    def diffUserLists( self, old, new ):
        """
            Return (list-of-added-users, list-of-removed-users).
        """
        plus, minus = list( new ), []

        for userid in list( old ):

            if userid in plus:
                plus.remove( userid )
            else:
                minus.append( userid )

        return ( plus, minus )

    security.declareProtected( CMFCorePermissions.View, 'listSupporters' )
    def listSupporters( self ):
        """
            Return a list (possibly empty) of user IDs of supporters
            assigned to this issue.
        """
        return self._supporters

    security.declareProtected( EditCollectorIssue, 'addSupporter' )
    def addSupporter( self, supporter ):
        """
            Add 'supporter' to the list of users who are assigned to
            this issue.
        """
        if supporter in self._supporters:
            raise ValueError, 'Already assigned: %s' % supporter

        supporters = list( self._supporters )
        supporters.append( supporter )
        self._supporters = tuple( supporters )

    security.declareProtected( EditCollectorIssue, 'removeSupporter' )
    def removeSupporter( self, supporter ):
        """
            Remove 'supporter' from the list of users who are assigned to
            this issue.
        """
        if supporter not in self._supporters:
            raise ValueError, 'Not assigned: %s' % supporter

        supporters = list( self._supporters )
        supporters.remove( supporter )
        self._supporters = tuple( supporters )

    security.declareProtected( EditCollectorIssue, 'setSupporters' )
    def setSupporters( self, supporters ):
        """
            Update our list of supporters;  return a list of strings
            indicating the changes (additions, removals).
        """
        changes = []

        added, removed = self.diffUserLists( self._supporters, supporters )
        self._supporters = tuple( supporters )

        if added:
            changes.append( 'added supporters: %s' % ' '.join( added ) )

        if removed:
            changes.append( 'removed supporters: %s' % ' '.join( removed ) )

        return changes

    security.declareProtected( EditCollectorIssue, 'clearSupporters' )
    def clearSupporters( self ):
        """
            Remove all supporters from an issue.
        """
        del self._supporters


    #
    #   Manage other interested parties.
    #
    security.declareProtected( CMFCorePermissions.View, 'listKibitzers' )
    def listKibitzers( self ):
        """
            Return a list (possibly empty) of user IDs of non-supporters
            who have subscribed to this issue.
        """
        return self._kibitzers

    security.declareProtected( EditCollectorIssue, 'addKibitzer' )
    def addKibitzer( self, kibitzer ):
        """
            Add 'kibitzer' to the list of users who are subscribed to
            this issue.
        """
        if kibitzer in self._kibitzers:
            raise ValueError, 'Already subscribed: %s' % kibitzer

        kibitzers = list( self._kibitzers )
        kibitzers.append( kibitzer )
        self._kibitzers = tuple( kibitzers )

    security.declareProtected( EditCollectorIssue, 'removeKibitzer' )
    def removeKibitzer( self, kibitzer ):
        """
            Remove 'kibitzer' from the list of users who are subscribed to
            this issue.
        """
        if kibitzer not in self._kibitzers:
            raise ValueError, 'Not subscribed: %s' % kibitzer

        kibitzers = list( self._kibitzers )
        kibitzers.remove( kibitzer )
        self._kibitzers = tuple( kibitzers )

    security.declareProtected( EditCollectorIssue, 'setKibitzers' )
    def setKibitzers( self, kibitzers ):
        """
            Update our list of kibitzers;  return a list of strings
            indicating the changes (additions, removals).
        """
        changes = []

        added, removed = self.diffUserLists( self._kibitzers, kibitzers )
        self._kibitzers = tuple( kibitzers )

        if added:
            changes.append( 'added kibitzers: %s' % ' '.join( added ) )

        if removed:
            changes.append( 'removed kibitzers: %s' % ' '.join( removed ) )

        return changes

    security.declareProtected( EditCollectorIssue, 'clearKibitzers' )
    def clearKibitzers( self ):
        """
            Remove all kibitzers from an issue.
        """
        del self._kibitzers

    #
    #   Manage the transcript.
    #
    security.declarePrivate( '_create_transcript' )
    def _create_transcript(self, description):
        """
            Create events and comments transcript, with initial entry.
        """
        addWebTextDocument( self
                          , TRANSCRIPT_NAME
                          , title=self.Title()
                          , description=description
                          )
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')

    security.declareProtected( CMFCorePermissions.View, 'getTranscript' )
    def getTranscript( self ):
        """
            Return the transcript
        """
        return self._getOb( TRANSCRIPT_NAME )

    get_transcript = getTranscript

    security.declareProtected( CMFCorePermissions.View, 'CookedBody' )
    def CookedBody( self ):
        """
            Render the transcript.
        """
        body = self.get_transcript().CookedBody()
        return uploadexp.sub(r'\1 <a href="%s/\2/view">\2</a>\3'
                             % self.absolute_url(),
                             body)

    security.declareProtected(CMFCorePermissions.View, 'cited_text')
    def cited_text(self):
        """
            Quote text for use in literal citations.
        """
        return util.cited_text( self.get_transcript().EditableBody() )
        
    #
    #   "Audit trail" management.
    #
    security.declarePrivate( '_incrementActionNumber')
    def _incrementActionNumber( self ):
        """
            Bump the "action" counter.
        """
        self._action_number += 1

    security.declareProtected( CMFCorePermissions.View, 'getActionNumber' )
    def getActionNumber( self ):
        """
            Return the sequence number of the most recent action.
        """
        return self._action_number
=======
        changes = []
        changed = self._changed

        transcript = self.get_transcript()
        text = text.replace('\r', '')
        changes += self._set_submitter_specs(submitter_id,
                                             submitter_name, submitter_email)
        if text is not None and text != transcript.text:
            changes.append('edited transcript')
            transcript.edit(text_format=self.TRANSCRIPT_FORMAT, text=text)
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
        if changed('version_info', version_info):
            changes.append('revised version_info')
            self.version_info = version_info

        if comment:
            changes.append('new comment')

        if not changes:
            return 'No changes.'

        self.action_number += 1

        username = str(getSecurityManager().getUser())

        if comment:
            comment = "\n\n" + comment
        else:
            comment = ''

        if not stealthy:
            transcript.edit(self.TRANSCRIPT_FORMAT,
                            self._entry_header('Edit', username)
                            + "\n\n"
                            + " Changes: " + ", ".join(changes)
                            + comment
                            + ((self.action_number > 1) and "\n" + RULE + "\n")
                            + transcript.EditableBody())
        else:
            transcript.edit(self.TRANSCRIPT_FORMAT,
                            transcript.EditableBody())            
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
>>>>>>> 1.39
    
    security.declareProtected(AddCollectorIssueFollowup, 'do_action')
    def do_action(self, action, comment,
                  assignees=None, file=None, fileid=None, filetype=None):
>>>>>>> 1.38.2.1
        """Execute an action, adding comment to the transcript."""

        action_number = self.action_number = self.action_number + 1
        username = str(getSecurityManager().getUser())

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
                                             assignees=self.listSupporters())

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

        (uploadmsg, fileid) = self._process_file(file, fileid,
                                                  filetype, comment)
        if uploadmsg:
            comment_header.append("\n" + uploadmsg)

        comment_header_str = "\n\n".join(comment_header) + "\n\n"

        transcript.edit(self.TRANSCRIPT_FORMAT,
                         comment_header_str
                         + comment
                         + ((action_number > 1)
                            and ("\n" + RULE + "\n")
                            or '')
                         + transcript.EditableBody())
        self.reindexObject()
        got = self._send_update_notice(action, username,
                                       orig_status, additions, removals,
                                       file=file, fileid=fileid)
        return got

<<<<<<< CollectorIssue.py
<<<<<<< CollectorIssue.py
    #
    #   File uploads.
    #
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
=======
    #
    #   File uploads.
    #
    def _process_file(self, file, fileid, filetype, comment):
        """Upload file to issue if it is substantial (has a name).
>>>>>>> 1.38.2.1

<<<<<<< CollectorIssue.py
    def upload_number(self):
        """ """
        return len(self)
=======
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
>>>>>>> 1.38.2.1

<<<<<<< CollectorIssue.py
    #
    #   E-mail notification.  XXX:  This belongs in the workflow!
    #
    security.declarePrivate( '_send_update_notice' )
=======
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
=======
    def _supporters_diff(self, orig_supporters):
        """Indicate supporter roster changes, relative to orig_supporters.
>>>>>>> 1.39

        Return (list-of-added-supporters, list-of-removed-supporters)."""
        plus, minus = list(self.assigned_to()), []
        for supporter in orig_supporters:
            if supporter in plus: plus.remove(supporter)
            else: minus.append(supporter)
        return (plus, minus)

<<<<<<< CollectorIssue.py
    #
    #   E-mail notification.  XXX:  This belongs in the workflow!
    #
    security.declarePrivate( '_send_update_notice' )
>>>>>>> 1.38.2.1
=======
>>>>>>> 1.39
    def _send_update_notice(self, action, actor,
                            orig_status=None, additions=None, removals=None,
                            file=None, fileid=None, lower=string.lower):
        """Send email notification about issue event to relevant parties."""

        action = string.capitalize(string.split(action, '_')[0])
        new_status = self.status()

        recipients = []

        # Who to notify:
        # 
        # We want to noodge only assigned supporters while it's being worked
        # on, ie assigned supporters are corresponding about it.  Otherwise,
        # either the dispatchers (managers) and assigned supporters get
        # notices, or everyone gets notices, depending on the collector's
        # .dispatching setting:
        #
        # - Requester always
        # - Person taking action always
        # - Supporters assigned to the issue always
        # - Managers or managers + all supporters (according to dispatching):
        #   - When in any state besides accepted (or accepted_confidential)
        #   - When being accepted (or accepted_confidential)
        #   - When is accepted (or accepted_confidential) and moving to
        #     another state 
        # - Any supporters being removed from the issue by the current action
        # - In addition, any destinations for the resulting state registered
        #   in state_email are included.
        #
        # We're liberal about allowing duplicates in the collection phase -
        # all duplicate addresses will be filtered out before actual send.

        candidates = [self.submitter_id, actor] + list(self.assigned_to())
        continuing_accepted = (orig_status
                               and
                               lower(orig_status) in ['accepted',
                                                      'accepted_confidential']
                               and
                               lower(new_status) in ['accepted',
                                                     'accepted_confidential'])
        if orig_status and not continuing_accepted:
            candidates.extend(self.aq_parent.managers)
            if not self.aq_parent.dispatching:
                candidates.extend(self.aq_parent.supporters)
        else:
            candidates.extend(self.assigned_to())

        if removals:
            # Notify supporters being removed from the issue (confirms 
            # their action, if they're resigning, and informs them if
            # manager is deassigning them).
            candidates.extend(removals)

        didids = []; gotemails = []
        for userid in candidates:
            if userid in didids:
                # Cull duplicates.
                continue
            didids.append(userid)
            name, email = util.get_email_fullname(self, userid)
            if (userid == self.submitter_id) and self.submitter_email:
                if self.submitter_email == email:
                    # Explicit one same as user preference - clear the
                    # explicit, so issue notification destination will track
                    # changes to the preference.
                    self.submitter_email = None
                else:
                    # Explicitly specified email overrides user pref email.
                    email = self.submitter_email
                if self.submitter_name:
                    name = self.submitter_name
            if email:
                if email in gotemails:
                    continue
                gotemails.append(email)
                recipients.append((name, email))

        if (self.state_email.has_key(new_status)
            and self.state_email[new_status]):
            for addr in re.split(", *| +", self.state_email[new_status]):
                se = ("_%s_ recipient" % new_status, addr)
                candidates.append(se)       # For recipients-debug
                if addr not in recipients:
                    recipients.append(se)

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

            body = self.get_transcript().text
            body = uploadexp.sub(r'\1 "\2"\n - %s/\2/view'
                                 % self.absolute_url(),
                                 body)
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
                          issue_url=self.absolute_url(),
                          body=body,
                          candidates=candidates)
            mh = self.MailHost
            try:
                mh.send(message)
            except:
                import sys
                err = sys.exc_info()
                return "Email notice error: '%s'"  % str(err[1])

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

    security.declareProtected(CMFCorePermissions.View, 'isConfidential')
    def isConfidential(self):
        """True if workflow has the issue marked confidential.

        (Security_related issues start confidential, and are made
        unconfidential on any completion.)"""
        wftool = getToolByName(self, 'portal_workflow')
<<<<<<< CollectorIssue.py
        return wftool and wftool.getInfoFor(self, 'confidential', 0)

=======
        return wftool.getInfoFor(self, 'confidential', 0)

<<<<<<< CollectorIssue.py
>>>>>>> 1.38.2.1
=======
    def _create_transcript(self, description):
        """Create events and comments transcript, with initial entry."""

        user = getSecurityManager().getUser()
        addWebTextDocument(self, TRANSCRIPT_NAME, description=description)
        it = self.get_transcript()
        it._setPortalTypeName('Collector Issue Transcript')
        it.title = self.title

>>>>>>> 1.39
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
        """Return actions valid according to workflow/application logic."""

        pa = getToolByName(self, 'portal_actions', None)
        allactions = pa.listFilteredActionsFor(self)
        return [entry['name']
                for entry in allactions.get('issue_workflow', [])]

    security.declareProtected(CMFCorePermissions.View, 'valid_actions_pairs')
    def valid_actions_pairs(self):
        """Return ordered (prettyname, rawname) valid workflow actions."""
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
<<<<<<< CollectorIssue.py
<<<<<<< CollectorIssue.py
        """
            Index the issue into the catalog(s) which are available,
            including both the "internal" catalog of the collector and
            the portal_catalog (either of which may not be present).

            'invisible' indicates that the issue should not show up
            in the catalog.
        """
        if not self.isInvisible():
            for catalog in self._listCatalogs():
                catalog.indexObject( self )
=======
        """
            Index the issue into the catalog(s) which are available,
            including both the "internal" catalog of the collector and
            the portal_catalog (either of which may not be present).

            'invisible' indicates that the issue should not show up
            in the catalog.
        """
        if not self.invisible:
            for catalog in self._listCatalogs():
                catalog.indexObject( self )
>>>>>>> 1.38.2.1
=======
        if self.invisible:
            return
        for i in (self._get_internal_catalog(),
                  getToolByName(self, 'portal_catalog', None)):
            if i is not None:
                i.indexObject(self)
>>>>>>> 1.39

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
<<<<<<< CollectorIssue.py
<<<<<<< CollectorIssue.py
        """
            Index the issue into the catalog(s) which are available,
            including both the "internal" catalog of the collector and
            the portal_catalog (either of which may not be present).

            'invisible' indicates that the issue should not show up
            in the catalog.
        """
        if not self.isInvisible():
            for catalog in self._listCatalogs( internal_only=internal_only ):
                catalog.reindexObject( self )

    security.declarePrivate( '_listCatalogs' )
    def _listCatalogs( self, internal_only=0 ):
        """
            Return a list of the catalogs into which the issue is indexed.
        """
        result = []
        parent = getattr( self, 'aq_parent', None )

        if parent is not None:

            try:
                internal = parent.get_internal_catalog()
            except AttributeError:
                pass
            else:
                result.append( internal )

=======
        """
            Index the issue into the catalog(s) which are available,
            including both the "internal" catalog of the collector and
            the portal_catalog (either of which may not be present).

            'invisible' indicates that the issue should not show up
            in the catalog.
        """
        if not self.invisible:
            for catalog in self._listCatalogs( internal_only=internal_only ):
                catalog.reindexObject( slef )

    security.declarePrivate( '_listCatalogs' )
    def _listCatalogs( self, internal_only=0 ):
        """
            Return a list of the catalogs into which the issue is indexed.
        """
        result = []
        parent = getattr( self, 'aq_parent', None )

        if parent is not None:

            try:
                internal = parent.get_internal_catalog()
            except AttributeError:
                pass
            else:
                result.append( internal )

>>>>>>> 1.38.2.1
=======
        if self.invisible:
            return
        catalogs = [self._get_internal_catalog()]
>>>>>>> 1.39
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
                + self.status() + ' '
                + (self.resolution or '') + ' '
                + self.version_info + ' '
                + ((self.security_related and 'security_related') or ''))

    def Subject(self):
        """The structured attributes."""
        return (self.topic,
                self.classification,
                self.importance,
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
<<<<<<< CollectorIssue.py
                      REQUEST=None
                     ):
=======
                      submitter_id=None,
                      submitter_name=None,
                      submitter_email=None,
                      kibitzers=None,
                      topic=None,
                      classification=None,
                      security_related=0,
                      importance=None,
                      version_info=None,
<<<<<<< CollectorIssue.py
                      invisible=0,
                      REQUEST=None
                     ):
>>>>>>> 1.38.2.1
=======
                      assignees=None,
                      file=None, fileid=None, filetype=None,
                      REQUEST=None):
>>>>>>> 1.39
    """Create a new issue in the collector.

    We return a string indicating any errors, or None if there weren't any."""

    it = CollectorIssue(id=id,
                        container=self,
                        title=title,
<<<<<<< CollectorIssue.py
                        description=description)
=======
                        description=description,
                        submitter_id=submitter_id,
                        submitter_name=submitter_name,
                        submitter_email=submitter_email,
                        kibitzers=kibitzers,
                        topic=topic,
                        classification=classification,
                        security_related=security_related,
                        importance=importance,
                        version_info=version_info,
<<<<<<< CollectorIssue.py
                        invisible=invisible
                       )
>>>>>>> 1.38.2.1
=======
                        assignees=assignees,
                        file=file, fileid=fileid, filetype=filetype)
>>>>>>> 1.39
    it = self._getOb(it.id)
    got = it.do_action('request', description, file, fileid, filetype)

    return got
