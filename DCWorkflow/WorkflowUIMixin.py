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
'''
Web-configurable workflow UI.
$Id$
'''
__version__='$Revision$'[11:-2]

from Globals import DTMLFile
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from utils import _dtmldir


class WorkflowUIMixin:
    '''
    '''

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_properties')
    manage_properties = DTMLFile('workflow_properties', _dtmldir)

    security.declareProtected(ManagePortal, 'setProperties')
    def setProperties(self, title, REQUEST=None):
        '''
        '''
        self.title = str(title)
        if REQUEST is not None:
            return self.manage_properties(
                REQUEST, manage_tabs_message='Properties changed.')

    _permissions_form = DTMLFile('workflow_permissions', _dtmldir)

    security.declareProtected(ManagePortal, 'manage_permissions')
    def manage_permissions(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._permissions_form(REQUEST,
                                      management_view='Permissions',
                                      manage_tabs_message=manage_tabs_message,
                                      )

    security.declareProtected(ManagePortal, 'addManagedPermission')
    def addManagedPermission(self, p, REQUEST=None):
        '''
        '''
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
        '''
        '''
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
        '''
        '''
        # possible_permissions is in AccessControl.Role.RoleManager.
        return list(self.possible_permissions())


Globals.InitializeClass(WorkflowUIMixin)
