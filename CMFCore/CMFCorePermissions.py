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
""" Declare named permissions used throughout the CMF.

$Id$
"""

import Products
from AccessControl import Permissions
from AccessControl.Permission import _registeredPermissions
from AccessControl.Permission import pname
from Globals import ApplicationDefaultPermissions

# General Zope permissions
AccessContentsInformation = Permissions.access_contents_information
ChangePermissions = Permissions.change_permissions
DeleteObjects = Permissions.delete_objects
FTPAccess = Permissions.ftp_access
ManageProperties = Permissions.manage_properties
UndoChanges = Permissions.undo_changes
View = Permissions.view
ViewManagementScreens = Permissions.view_management_screens

def setDefaultRoles(permission, roles):
    '''
    Sets the defaults roles for a permission.
    '''
    # XXX This ought to be in AccessControl.SecurityInfo.
    registered = _registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = pname(permission)
        setattr(ApplicationDefaultPermissions, mangled, roles)

# Note that we can only use the default Zope roles in calls to
# setDefaultRoles().  The default Zope roles are:
# Anonymous, Manager, and Owner.

#
# CMF Base Permissions
#

ListFolderContents = 'List folder contents'
setDefaultRoles( ListFolderContents, ( 'Manager', 'Owner' ) )

ListUndoableChanges = 'List undoable changes'
setDefaultRoles( ListUndoableChanges, ('Manager',) )  # + Member

AccessInactivePortalContent = 'Access inactive portal content'
setDefaultRoles(AccessInactivePortalContent, ('Manager',))

ModifyCookieCrumblers = 'Modify Cookie Crumblers'
setDefaultRoles(ModifyCookieCrumblers, ('Manager',))

ReplyToItem = 'Reply to item'
setDefaultRoles(ReplyToItem, ('Manager',))  # + Member

ManagePortal = 'Manage portal'
setDefaultRoles(ManagePortal, ('Manager',))

ModifyPortalContent = 'Modify portal content'
setDefaultRoles(ModifyPortalContent, ('Manager',))

ListPortalMembers = 'List portal members'
setDefaultRoles( ListPortalMembers, ('Manager',) )  # + Member

AddPortalFolders = 'Add portal folders'
setDefaultRoles(AddPortalFolders, ('Owner','Manager'))  # + Member

AddPortalContent = 'Add portal content'
setDefaultRoles(AddPortalContent, ('Owner','Manager',))  # + Member

AddPortalMember = 'Add portal member'
setDefaultRoles(AddPortalMember, ('Anonymous', 'Manager',))

SetOwnPassword = 'Set own password'
setDefaultRoles(SetOwnPassword, ('Manager',))  # + Member

SetOwnProperties = 'Set own properties'
setDefaultRoles(SetOwnProperties, ('Manager',))  # + Member

MailForgottenPassword = 'Mail forgotten password'
setDefaultRoles(MailForgottenPassword, ('Anonymous', 'Manager',))


#
# Workflow Permissions
#

RequestReview = 'Request review'
setDefaultRoles(RequestReview, ('Owner', 'Manager',))

ReviewPortalContent = 'Review portal content'
setDefaultRoles(ReviewPortalContent, ('Manager',))  # + Reviewer

AccessFuturePortalContent = 'Access future portal content'
setDefaultRoles(AccessFuturePortalContent, ('Manager',))  # + Reviewer

