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
""" Web-configurable workflow UI.

$Id$
"""

from Globals import DTMLFile
import Globals
from AccessControl import ClassSecurityInfo
from Acquisition import aq_get
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Guard import Guard
from utils import _dtmldir

try:
    # If base_cms exists, include the roles it defines.
    from Products.base_cms.permissions import getDefaultRolePermissionMap
except ImportError:
    def getDefaultRolePermissionMap():
        return {}


class WorkflowUIMixin:
    '''
    '''

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_properties')
    manage_properties = DTMLFile('workflow_properties', _dtmldir)
    manage_groups = PageTemplateFile('workflow_groups.pt', _dtmldir)

    security.declareProtected(ManagePortal, 'setProperties')
    def setProperties(self, title, manager_bypass=0, props=None, REQUEST=None):
        """Sets basic properties.
        """
        self.title = str(title)
        self.manager_bypass = manager_bypass and 1 or 0
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.creation_guard = g
        else:
            self.creation_guard = None
        if REQUEST is not None:
            return self.manage_properties(
                REQUEST, manage_tabs_message='Properties changed.')

    _permissions_form = DTMLFile('workflow_permissions', _dtmldir)

    security.declareProtected(ManagePortal, 'manage_permissions')
    def manage_permissions(self, REQUEST, manage_tabs_message=None):
        """Displays the form for choosing which permissions to manage.
        """
        return self._permissions_form(REQUEST,
                                      management_view='Permissions',
                                      manage_tabs_message=manage_tabs_message,
                                      )

    security.declareProtected(ManagePortal, 'addManagedPermission')
    def addManagedPermission(self, p, REQUEST=None):
        """Adds to the list of permissions to manage.
        """
        if p in self.permissions:
            raise ValueError, 'Already a managed permission: ' + p
        if REQUEST is not None and p not in self.getPossiblePermissions():
            raise ValueError, 'Not a valid permission name:' + p
        self.permissions = self.permissions + (p,)
        if REQUEST is not None:
            return self.manage_permissions(
                REQUEST, manage_tabs_message='Permission added.')

    security.declareProtected(ManagePortal, 'delManagedPermissions')
    def delManagedPermissions(self, ps, REQUEST=None):
        """Removes from the list of permissions to manage.
        """
        if ps:
            l = list(self.permissions)
            for p in ps:
                l.remove(p)
            self.permissions = tuple(l)
        if REQUEST is not None:
            return self.manage_permissions(
                REQUEST, manage_tabs_message='Permission(s) removed.')

    security.declareProtected(ManagePortal, 'getPossiblePermissions')
    def getPossiblePermissions(self):
        """Returns the list of all permissions that can be managed.
        """
        # possible_permissions is in AccessControl.Role.RoleManager.
        return list(self.possible_permissions())


    def _getGroupFolder(self):
        try:
            return aq_get(self, "acl_groups", None, 1)
        except AttributeError:
            pass
        return None

    security.declareProtected(ManagePortal, 'getGroups')
    def getGroups(self):
        """Returns the names of groups managed by this workflow.
        """
        return tuple(self.groups)

    security.declareProtected(ManagePortal, 'getAvailableGroups')
    def getAvailableGroups(self):
        """Returns a list of available group names.
        """
        gf = self._getGroupFolder()
        if gf is None:
            return ()
        r = []
        r.extend(gf.getDynamicGroups())
        r.extend(gf.getStaticGroups())
        return [g.getId() for g in r]

    security.declareProtected(ManagePortal, 'addGroup')
    def addGroup(self, group, RESPONSE=None):
        """Adds a group by name.
        """
        gf = self._getGroupFolder()
        g = gf.getGroupById(group)
        if g is None:
            raise ValueError(group)
        self.groups = self.groups + (group,)
        if RESPONSE is not None:
            RESPONSE.redirect(
                "%s/manage_groups?manage_tabs_message=Added+group."
                % self.absolute_url())

    security.declareProtected(ManagePortal, 'delGroups')
    def delGroups(self, groups, RESPONSE=None):
        """Removes groups by name.
        """
        self.groups = tuple([g for g in self.groups if g not in groups])
        if RESPONSE is not None:
            RESPONSE.redirect(
                "%s/manage_groups?manage_tabs_message=Groups+removed."
                % self.absolute_url())

    security.declareProtected(ManagePortal, 'getAvailableRoles')
    def getAvailableRoles(self):
        """Returns the acquired roles mixed with base_cms roles.
        """
        roles = list(self.valid_roles())
        for role in getDefaultRolePermissionMap().keys():
            if role not in roles:
                roles.append(role)
        roles.sort()
        return roles

    security.declareProtected(ManagePortal, 'getRoles')
    def getRoles(self):
        """Returns the list of roles managed by this workflow.
        """
        roles = self.roles
        if roles is not None:
            return roles
        roles = getDefaultRolePermissionMap().keys()
        if roles:
            # Map the base_cms roles by default.
            roles.sort()
            return roles
        return self.valid_roles()

    security.declareProtected(ManagePortal, 'setRoles')
    def setRoles(self, roles, RESPONSE=None):
        """Changes the list of roles mapped to groups by this workflow.
        """
        avail = self.getAvailableRoles()
        for role in roles:
            if role not in avail:
                raise ValueError(role)
        self.roles = tuple(roles)
        if RESPONSE is not None:
            RESPONSE.redirect(
                "%s/manage_groups?manage_tabs_message=Roles+changed."
                % self.absolute_url())

    security.declareProtected(ManagePortal, 'getGuard')
    def getGuard(self):
        """Returns the initiation guard.

        If no init guard has been created, returns a temporary object.
        """
        if self.creation_guard is not None:
            return self.creation_guard
        else:
            return Guard().__of__(self)  # Create a temporary guard.


Globals.InitializeClass(WorkflowUIMixin)
