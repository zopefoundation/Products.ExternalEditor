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

"""Implement the Collector issue-container content type."""

import os, urllib
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile, package_home

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo, Permission
from AccessControl import getSecurityManager

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.CatalogTool import CatalogTool

from Products.CMFDefault.SkinnedFolder import SkinnedFolder

import util

# Import permission names
from Products.CMFCore import CMFCorePermissions
from CollectorPermissions import *

from CollectorIssue import addCollectorIssue, CollectorIssue

INTERNAL_CATALOG_ID = 'collector_catalog'

# Factory type information -- makes Events objects play nicely
# with the Types Tool (portal_types)
factory_type_information = (
    {'id': 'Collector',
     'content_icon': 'collector_icon.gif',
     'meta_type': 'CMF Collector',
     'description': ('A Collector is a facility for tracking bug reports and'
                     ' other issues.'), 
     'product': 'CMFCollector',
     'factory': 'addCollector',
     'allowed_content_types': ('CollectorIssue', 'CollectorCatalog'), 
     'immediate_view': 'collector_edit_form',
     'actions': ({'id': 'view',
                  'name': 'Browse',
                  'action': 'collector_contents',
                  'permissions': (ViewCollector,)},
                 {'id': 'addissue',
                  'name': 'New Issue',
                  'action': 'collector_add_issue_form',
                  'permissions': (AddCollectorIssue,)},
                 {'id': 'edit',
                  'name': 'Configure',
                  'action': 'collector_edit_form',
                  'permissions': (ManageCollector,)},
                 ),
     },
    )

_dtmldir = os.path.join(package_home(globals()), 'dtml')
addCollectorForm = DTMLFile('addCollectorForm', _dtmldir, Kind='CMF Collector')

class Collector(SkinnedFolder):
    """Collection of IssueBundles."""

    meta_type = 'CMF Collector'
    effective_date = expiration_date = None
    
    DEFAULT_IMPORTANCES = ['medium', 'critical', 'low']
    DEFAULT_CLASSIFICATIONS = ['bug', 'bug+solution',
                               'feature', 'feature+solution',
                               'doc', 'test']
    DEFAULT_VERSION_INFO_SPIEL = (
        "Version details; also include related info like browser,"
        " webserver, database, python, OS, etc.")
    version_info_spiel = DEFAULT_VERSION_INFO_SPIEL

    security = ClassSecurityInfo()

    abbrev = 'CLTR'

    managers = ()
    dispatching = 1
    # participation modes: 'staff', 'authenticated', 'anyone'
    participation = 'staff'

    # state_email - a dictionary pairing state names with email destinations
    # for all notifications occuring within that state.
    state_email = {}

    batch_size = 10

    _properties=({'id':'title', 'type': 'string', 'mode':'w'},
                 {'id':'last_issue_id', 'type': 'int', 'mode':'w'},
                 {'id':'batch_size', 'type': 'int', 'mode':'w'},
                 )

    def __init__(self, id, title='', description='', abbrev='',
                 email=None,
                 topics=None, classifications=None, importances=None,
                 managers=None, supporters=None, dispatching=None,
                 version_info_spiel=None):

        SkinnedFolder.__init__(self, id, title)

        self._setup_internal_catalog()

        self.last_issue_id = 0

        self.description = description
        self.abbrev = abbrev

        username = str(getSecurityManager().getUser())
        util.add_local_role(self, username, 'Manager')
        util.add_local_role(self, username, 'Owner')
        if managers is None:
            if username: managers = [username]
            else: managers = []
        elif username and username not in managers:
            managers.append(username)
        self.managers = managers
        if supporters is None:
            supporters = []
        self.supporters = supporters
        self._adjust_staff_roles(no_reindex=1)

        # XXX We need to ensure *some* collector email addr...
        self.email = email

        if topics is None:
            self.topics = ['Zope', 'Collector', 'Database',
                           'Catalog', 'ZServer']
        else: self.topics = topics

        if classifications is None:
            self.classifications = self.DEFAULT_CLASSIFICATIONS
        else: self.classifications = classifications

        if importances is None:
            self.importances = self.DEFAULT_IMPORTANCES
        else: self.importances = importances

        if version_info_spiel is None:
            self.version_info_spiel = self.DEFAULT_VERSION_INFO_SPIEL
        else: self.version_info_spiel = version_info_spiel

        return self

    def _setup_internal_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = CollectorCatalog()
        self._setObject(catalog.id, catalog)

    security.declareProtected(CMFCorePermissions.View, 'get_internal_catalog')
    def get_internal_catalog(self):
        """ """
        return self._getOb(INTERNAL_CATALOG_ID)
        

    security.declareProtected(AddCollectorIssue, 'new_issue_id')
    def new_issue_id(self):
        """Return a new issue id, incrementing the internal counter."""
        lastid = self.last_issue_id = self.last_issue_id + 1
        return str(lastid)

    security.declareProtected(AddCollectorIssue, 'add_issue')
    def add_issue(self,
                  title=None,
                  description=None,
                  security_related=None,
                  submitter_name=None,
                  submitter_email=None,
                  kibitzers=None,
                  topic=None,
                  importance=None,
                  classification=None,
                  version_info=None,
                  assignees=None,
                  file=None, fileid=None, filetype=None):
        """Create a new collector issue."""
        id = self.new_issue_id()
        submitter_id = str(getSecurityManager().getUser())
        
        err = addCollectorIssue(self,
                                id,
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
                                version_info=version_info,
                                assignees=assignees,
                                file=file, fileid=fileid, filetype=filetype)
        return id, err


    security.declareProtected(ManageCollector, 'edit')
    def edit(self, title=None, description=None,
             abbrev=None, email=None,
             managers=None, supporters=None, dispatching=None,
             participation=None,
             state_email=None,
             topics=None, classifications=None,
             importances=None,
             version_info_spiel=None):

        changes = []
        staff_changed = 0
        userid = str(getSecurityManager().getUser())

        if title is not None and title != self.title:
            self.title = title
            changes.append("Title")

        if description is not None and self.description != description:
            self.description = description
            changes.append("Description")

        if abbrev is not None and self.abbrev != abbrev:
            self.abbrev = abbrev
            changes.append("Abbrev")

        if email is not None and self.email != email:
            self.email = email
            changes.append("Email")

        if not self.email:
            raise ValueError, ('<strong>'
                               '<font color="red">'
                               'The collector <em>must</em>'
                               ' have an email address'
                               '</font>'
                               '</strong>')

        if managers is not None or not self.managers:
            # XXX Vette managers - they must exist, etc.
            x = filter(None, managers)
            if not self.managers:
                changes.append("Managers can't be empty - including initial"
                               " owner")
                # Somehow we arrived here with self.managers empty - reinstate
                # at least the owner, if any found, else the current manager.
                owners = self.users_with_local_role('Owner')
                if owners:
                    x.extend(owners)
                else:
                    x.append(userid)
            elif ((userid in self.managers)
                  and (userid not in x)):
                changes.append("Managers cannot de-enlist themselves")
                x.append(userid)
            if util.sorted(self.managers) != util.sorted(x):
                changes.append("Managers")
                self.managers = x
                staff_changed = 1

        if supporters is not None:
            # XXX Vette supporters - they must exist, etc.
            x = filter(None, supporters)
            if util.sorted(self.supporters) != util.sorted(x):
                changes.append("Supporters")
                self.supporters = x
                staff_changed = 1

        if staff_changed:
            changes.extend(self._adjust_staff_roles())

        if dispatching is not None and self.dispatching != dispatching:
            self.dispatching = dispatching
            changes.append("Dispatching %s"
                           % ((dispatching and "on") or "off"))

        if participation is not None and self.participation != participation:
            self._adjust_participation_mode(participation)
            changes.append("Participation => '%s'" % participation)

        if state_email is not None:
            changed = 0
            # Use a new dict, to ensure it's divorced from shared class
            # variable hood.
            se = {}
            if type(self.state_email) != type({}):
                # Backwards-compat hack.  Convert back to dictionary...
                d = {}
                for k, v in self.state_email.items(): d[k] = v
                self.state_email = d
            se.update(self.state_email)
            for k, v in state_email.items():
                current_setting = se.get(k, None)
                if ( ((not current_setting) and v)
                    or (current_setting and (current_setting != v)) ):
                    changed = 1
                    if not v:
                        del se[k]
                    else:
                        se[k] = v
            if changed:
                self.state_email = se
                changes.append("State email")

        if topics is not None:
            x = filter(None, topics)
            if self.topics != x:
                self.topics = x
                changes.append("Topics")

        if classifications is not None:
            x = filter(None, classifications)
            if self.classifications != x:
                self.classifications = x
                changes.append("Classifications")

        if importances is not None:
            x = filter(None, importances)
            if self.importances != x:
                self.importances = x
                changes.append("Importance")

        if version_info_spiel is not None:
            if self.version_info_spiel != version_info_spiel:
                self.version_info_spiel = version_info_spiel
                changes.append("Version Info spiel")

        return ", ".join(changes)

    def _adjust_staff_roles(self, no_reindex=0):
        """Adjust local-role assignments to track staff roster settings.
        Ie, ensure: only designated supporters and managers have 'Reviewer'
        local role, only designated managers have 'Manager' local role.

        We reindex the issues if any local role changes occur, so
        allowedRolesAndUsers catalog index tracks.

        We return a list of changes (or non-changes)."""

        managers = self.managers
        supporters = self.supporters
        change_notes = []
        changed = 0

        if not managers:
            # Something is awry.  Managers are not allowed to remove
            # themselves from the managers roster, and only managers should be
            # able to adjust the roles, so:
            change_notes.append("Populated empty managers roster")
            changed = 1
            self.managers = managers = [str(getSecurityManager().getUser())]
        if util.users_for_local_role(self, managers, 'Manager'):
            changed = 1
        if util.users_for_local_role(self, managers + supporters, 'Reviewer'):
            changed = 1
        if changed and not no_reindex:
            self._reindex_issues()

        return change_notes

    def _adjust_participation_mode(self, mode):
        """Set role privileges according to participation mode."""

        target_roles = ['Reviewer', 'Manager', 'Owner']

        if mode == 'authenticated':
            target_roles = target_roles + ['Authenticated']
        elif mode == 'anyone':
            target_roles = target_roles + ['Authenticated', 'Anonymous']

        self.manage_permission(AddCollectorIssueFollowup,
                               roles=target_roles,
                               acquire=1)

        self.participation = mode

    security.declareProtected(ManageCollector, 'reinstate_catalog')
    def reinstate_catalog(self, internal_only=1):
        """Recreate and reload internal catalog, to accommodate drastic
        changes."""
        try:
            self._delObject(INTERNAL_CATALOG_ID)
        except AttributeError:
            pass
        self._setup_internal_catalog()
        self._reindex_issues(internal_only=internal_only)

    def _reindex_issues(self, internal_only=1):
        """For, eg, allowedRolesAndUsers recompute after local_role changes.

        We also make sure that the AddCollectorIssueFollowup permission
        acquires (old workflows controlled this).  This isn't exactly the
        right place, but it is an expedient one."""

        for i in self.objectValues(spec='CMF Collector Issue'):

            # Ensure the issue acquires AddCollectorIssueFollowup permission.
            for m in i.ac_inherited_permissions(1):
                if m[0] == AddCollectorIssueFollowup:
                    perm = Permission.Permission(m[0], m[1], i)
                    roles = perm.getRoles()
                    if type(roles) == type(()):
                        perm.setRoles(list(roles))

            i.reindexObject(internal_only=internal_only)

    security.declareProtected(ManageCollector, 'issue_states')
    def issue_states(self):
        """Return a sorted list of potential states for issues."""
        # We use a stub issue (which we create, the first time) in order to
        # get the workflow states.  Kinda yucky - would be nice if the
        # workflow provided more direct introspection.
        got = []
        if hasattr(self, 'stub'):
            sample = self['stub']
        else:
            sample = CollectorIssue('stub', self, invisible=1)
        for wf in self.portal_workflow.getWorkflowsFor(sample):
            got.extend([x.id for x in wf.states.values()])
        got.sort()
        return got

    security.declareProtected(CMFCorePermissions.View, 'Subject')
    def Subject(self):
        return self.topics

    security.declareProtected(CMFCorePermissions.View, 'length')
    def length(self):
        """Use length protocol."""
        return self.__len__()
        
    def __len__(self):
        """length() protocol method."""
        return len(self.objectIds()) - 1

    def __repr__(self):
        return ("<%s %s (%d issues) at 0x%s>"
                % (self.__class__.__name__, `self.id`, len(self),
                   hex(id(self))[2:]))

InitializeClass(Collector)
    
catalog_factory_type_information = (
    {'id': 'Collector Catalog',
     'content_icon': 'collector_icon.gif',
     'meta_type': 'CMF Collector Catalog',
     'description': ('Internal catalog.'), 
     'product': 'CMFCollector',
     'factory': None,
     'immediate_view': None},)

class CollectorCatalog(CatalogTool):

    id = INTERNAL_CATALOG_ID
    meta_type = 'CMF Collector Catalog'
    portal_type = 'Collector Catalog'

    def enumerateIndexes(self):
        standard = CatalogTool.enumerateIndexes(self)
        custom = (('status', 'FieldIndex'),
                  ('topic', 'FieldIndex'),
                  ('classification', 'FieldIndex'),
                  ('importance', 'FieldIndex'),
                  ('security_related', 'FieldIndex'),
                  ('confidential', 'FieldIndex'),
                  ('resolution', 'TextIndex'),
                  ('submitter_id', 'FieldIndex'),
                  ('submitter_email', 'FieldIndex'),
                  ('version_info', 'TextIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('upload_number', 'KeywordIndex')
                  )
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('status',
                  'submitter_id',
                  'topic',
                  'classification',
                  'importance',
                  'security_related',
                  'confidential',
                  'version_info',
                  'assigned_to',
                  'uploads',
                  'action_number',
                  'upload_number',
                  )
        return standard + custom

InitializeClass(CollectorCatalog)


# XXX Enable use of pdb.set_trace() in python scripts
#ModuleSecurityInfo('pdb').declarePublic('set_trace')

def addCollector(self, id, title='', description='', abbrev='',
                 topics=None, classifications=None, importances=None, 
                 managers=None, supporters=None, dispatching=None,
                 version_info_spiel=None,
                 REQUEST=None):
    """
    Create a collector.
    """
    it = Collector(id, title=title, description=description, abbrev=abbrev,
                   topics=topics, classifications=classifications,
                   managers=managers, supporters=supporters,
                   dispatching=dispatching,
                   version_info_spiel=version_info_spiel)
    self._setObject(id, it)
    it = self._getOb(id)
    it._setPortalTypeName('Collector')

    it.manage_permission(ManageCollector, roles=['Manager', 'Owner'],
                         acquire=1)
    it.manage_permission(EditCollectorIssue,
                         roles=['Reviewer'],
                         acquire=1)
    it.manage_permission(AddCollectorIssueFollowup,
                         roles=['Reviewer', 'Manager', 'Owner'],
                         acquire=1)
    it.manage_permission(CMFCorePermissions.AccessInactivePortalContent,
                         roles=['Anonymous', 'Reviewer', 'Manager', 'Owner'],
                         acquire=1)
    it.manage_permission(CMFCorePermissions.AccessFuturePortalContent,
                         roles=['Anonymous', 'Reviewer', 'Manager', 'Owner'],
                         acquire=1)
    if REQUEST is not None:
        try:    url=self.DestinationURL()
        except: url=REQUEST['URL1']
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
    return id
