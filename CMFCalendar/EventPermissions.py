from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Event Related Permissions into one place
AddEvents = 'Add portal events'
ChangeEvents = 'Change portal events'

# Set up default roles for permissions
setDefaultRoles(AddEvents, ('Manager', 'Owner', 'Member'))
setDefaultRoles(ChangeEvents, ('Manager', 'Owner',))
