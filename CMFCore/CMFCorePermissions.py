
# A first attempt at getting all of the Permissions used in the CMFCore
# into a single defined place.

# General Zope permissions
View = 'View'
AccessContentsInformation = 'Access contents information'
UndoChanges = 'Undo changes'
ChangePermissions = 'Change permissions'
ViewManagementScreens = 'View management screens'
ManageProperties = 'Manage properties'

# CMF Base Permissions
AccessInactivePortalContent = 'Access inactive portal content'
ModifyCookieCrumblers = 'Modify Cookie Crumblers'
ReplyToItem = 'Reply to item'
ManagePortal = 'Manage portal'
ReviewPortalContent = 'Review portal content'
ModifyPortalContent = 'Modify portal content'
AddPortalFolders = 'Add portal folders'
AddPortalContent = 'Add portal content'
AddPortalMember = 'Add portal member'
SetOwnPassword = 'Set own password'
SetOwnProperties = 'Set own properties'
MailForgottenPassword = 'Mail forgotten password'


# Workflow Permissions
RequestReview = 'Request review'
ReviewPortalContent = 'Review portal content'
AccessFuturePortalContent = 'Access future portal content'


import Globals, AccessControl, Products

def setDefaultRoles(permission, roles):
    '''
    Sets the defaults roles for a permission.
    '''
    # XXX This ought to be in AccessControl.SecurityInfo.
    registered = AccessControl.Permission._registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = AccessControl.Permission.pname(permission)
        setattr(Globals.ApplicationDefaultPermissions, mangled, roles)


setDefaultRoles(ManagePortal, ('Manager',))
setDefaultRoles(ModifyPortalContent, ('Manager',))
