from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Topic Related Permissions into one place
AddTopics = 'Add portal topics'
ChangeTopics = 'Change portal topics'

# Set up default roles for permissions
setDefaultRoles(AddTopics, ('Manager',))
setDefaultRoles(ChangeTopics, ('Manager', 'Owner',))

