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

"""Implement the Collector issue-container content type."""

import os, urllib
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile, package_home

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
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

from CollectorIssue import addCollectorIssue

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
    DEFAULT_SEVERITIES = ['normal', 'critical', 'major', 'minor']
    DEFAULT_CLASSIFICATIONS = ['bug', 'bug+solution', 'feature', 'doc', 'test']
    DEFAULT_VERSIONS = ['current', 'development', 'old', 'unique']
    DEFAULT_OTHER_VERSIONS_SPIEL = (
        "Pertinent other-system details, eg browser, webserver,"
        " database, python, OS, etc.") 

    security = ClassSecurityInfo()

    abbrev = 'CLTR'

    def __init__(self, id, title='', description='', abbrev='',
                 email=None,
                 topics=None, classifications=None,
                 importances=None, severities=None,
                 supporters=None,
                 versions=None, other_versions_spiel=None):

        SkinnedFolder.__init__(self, id, title)

        self._setup_internal_catalog()

        self.last_issue_id = 0

        self.description = description
        self.abbrev = abbrev

        username = str(getSecurityManager().getUser())
        util.add_local_role(self, username, 'Manager')
        util.add_local_role(self, username, 'Owner')
        if supporters is None:
            if username: supporters = [username]
            else: supporters = []
        self._adjust_supporters_roster(supporters)
        self.supporters = supporters

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

        if severities is None:
            self.severities = self.DEFAULT_SEVERITIES
        else: self.severities = severities

        if versions is None:
            self.versions = self.DEFAULT_VERSIONS
        else: self.versions = versions

        if other_versions_spiel is None:
            self.other_versions_spiel = self.DEFAULT_OTHER_VERSIONS_SPIEL
        else: self.other_versions_spiel = other_versions_spiel

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
                  submitter=None,
                  security_related=None,
                  kibitzers=None,
                  topic=None,
                  importance=None,
                  classification=None,
                  severity=None,
                  reported_version=None,
                  other_version_info=None,
                  assignees=None,
                  file=None, fileid=None, filetype=None):
        """Instigate a new collector issue."""
        id = self.new_issue_id()
        submitter_id = str(getSecurityManager().getUser())
        
        addCollectorIssue(self,
                          id,
                          title=title,
                          description=description,
                          submitter_id=submitter_id,
                          submitter_name=submitter,
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


    security.declareProtected(ManageCollector, 'edit')
    def edit(self, title=None, description=None,
             abbrev=None, email=None,
             supporters=None,
             topics=None, classifications=None,
             importances=None, severities=None,
             versions=None, other_versions_spiel=None):
        changed = reindex = 0
        if title is not None and title != self.title:
            self.title = title
            changed = 1
        if description is not None and self.description != description:
            self.description = description
            changed = 1
        if abbrev is not None and self.abbrev != abbrev:
            self.abbrev = abbrev
            changed = 1
        if email is not None and self.email != email:
            self.email = email
            changed = 1
        if supporters is not None:
            # XXX Vette supporters - they must exist, etc.
            x = filter(None, supporters)
            if self.supporters != x:
                self._adjust_supporters_roster(x)
                self.supporters = x
                changed = 1
                reindex = 1
        if topics is not None:
            x = filter(None, topics)
            if self.topics != x:
                self.topics = x
                changed = 1
        if classifications is not None:
            x = filter(None, classifications)
            if self.classifications != x:
                self.classifications = x
                changed = 1
        if importances is not None:
            x = filter(None, importances)
            if self.importances != x:
                self.importances = x
                changed = 1
        if versions is not None:
            x = filter(None, versions)
            if self.versions != x:
                self.versions = x
                changed = 1

        if versions is not None:
            x = filter(None, versions)
            if self.versions != x:
                self.versions = x
                changed = 1
        if other_versions_spiel is not None:
            if self.other_versions_spiel != other_versions_spiel:
                self.other_versions_spiel = other_versions_spiel
                changed = 1

        if reindex:
            self._reindex_issues()

        return changed

    def _adjust_supporters_roster(self, new_roster):
        """Adjust supporters local-role assignments to track roster changes.
        Ie, ensure all and only designated supporters have 'Reviewer' local
        role."""

        already = []
        # Remove 'Reviewer' local role from anyone having it not on new_roster:
        for u in self.users_with_local_role('Reviewer'):
            if u in new_roster:
                already.append(u)
            else:
                # Remove the 'Reviewer' local role:
                roles = list(self.get_local_roles_for_userid(u))
                roles.remove('Reviewer')
                if roles:
                    self.manage_setLocalRoles(u, roles)
                else:
                    self.manage_delLocalRoles([u])
        # Add 'Reviewer' local role to anyone on new_roster that lacks it:
        for u in new_roster:
            if u not in already:
                util.add_local_role(self, u, 'Reviewer')

    security.declareProtected(ManageCollector, 'reinstate_catalog')
    def reinstate_catalog(self, internal_only=0):
        """Recreate and reload internal catalog, to accommodate drastic
        changes."""
        try:
            self._delObject(INTERNAL_CATALOG_ID)
        except AttributeError:
            pass
        self._setup_internal_catalog()
        for i in self.objectValues(spec='CMF Collector Issue'):
            # Normalize security_related setting
            if i.security_related not in [0, 1]:
                i.security_related = (i.security_related and 1) or 0
        self._reindex_issues(internal_only=internal_only)

    def _reindex_issues(self, internal_only=0):
        """For, eg, allowedRolesAndUsers recompute after local_role changes."""
        for i in self.objectValues(spec='CMF Collector Issue'):
            i.reindexObject(internal_only=internal_only)

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
                  ('submitter_email', 'TextIndex'),
                  ('version_info', 'TextIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('upload_number', 'KeywordIndex')
                  )
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('status',
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
ModuleSecurityInfo('pdb').declarePublic('set_trace')

def addCollector(self, id, title='', description='', abbrev='',
                 topics=None, classifications=None,
                 importances=None, severities=None,
                 supporters=None,
                 versions=None, other_versions_spiel=None,
                 REQUEST=None):
    """
    Create a collector.
    """
    it = Collector(id, title=title, description=description, abbrev=abbrev,
                   topics=topics, classifications=classifications,
                   supporters=supporters, 
                   versions=versions,
                   other_versions_spiel=other_versions_spiel)
    self._setObject(id, it)
    it = self._getOb(id)
    it._setPortalTypeName('Collector')

    it.manage_permission(ManageCollector, roles=['Owner'], acquire=1)
    it.manage_permission(EditCollectorIssue,
                         roles=['Reviewer'],
                         acquire=1)
    it.manage_permission(AddCollectorIssueFollowup,
                         roles=['Reviewer', 'Owner'],
                         acquire=1)
    if REQUEST is not None:
        try:    url=self.DestinationURL()
        except: url=REQUEST['URL1']
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
    return id
        
