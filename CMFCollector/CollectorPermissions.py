from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

# Gathering Event Related Permissions into one place
ViewCollector = CMFCorePermissions.View
AddCollector = 'Add portal collector'
ManageCollector = 'Add portal collector'
AddCollectorIssue = 'Add collector issue'
AddCollectorIssueComment = 'Add collector issue comment'
AddCollectorIssueArtifact = 'Add collector issue artifact'
EditCollectorIssue = 'Edit collector issue'
SupportIssue = 'Support collector issue'

# Set up default roles for permissions
setDefaultRoles(AddCollector, CMFCorePermissions.AddPortalContent)
setDefaultRoles(ManageCollector,
                ('Manager', 'Owner'))
setDefaultRoles(AddCollectorIssue,
                ('Anonymous', 'Manager', 'Reviewer', 'Owner'))
setDefaultRoles(AddCollectorIssueComment,
                ('Manager', 'Reviewer', 'Owner'))
setDefaultRoles(AddCollectorIssueArtifact,
                ('Manager', 'Reviewer', 'Owner'))
setDefaultRoles(EditCollectorIssue,
                ('Manager', 'Reviewer'))
setDefaultRoles(SupportIssue,
                ('Manager', 'Reviewer'))
