""" CMFCollector product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('Products.CMFCollector.permissions')

security.declarePublic('View')
from Products.CMFCore.permissions import View

security.declarePublic('AddPortalContent')
from Products.CMFCore.permissions import AddPortalContent

security.declarePublic('AccessInactivePortalContent')
from Products.CMFCore.permissions import AccessInactivePortalContent

security.declarePublic('AccessFuturePortalContent')
from Products.CMFCore.permissions import AccessFuturePortalContent

security.declarePublic('ModifyPortalContent')
from Products.CMFCore.permissions import ModifyPortalContent

security.declarePublic('ViewCollector')
ViewCollector = View

security.declarePublic('ViewCollector')
AddCollector = 'Add portal collector'
setDefaultRoles(AddCollector, ('Manager', 'Owner'))

security.declarePublic('ManageCollector')
ManageCollector = 'Add portal collector'
setDefaultRoles(ManageCollector, ('Manager', 'Owner'))

security.declarePublic('AddCollectorIssue')
AddCollectorIssue = 'Add collector issue'
setDefaultRoles(AddCollectorIssue,
                ('Anonymous', 'Manager', 'Reviewer', 'Owner'))

security.declarePublic('AddCollectorIssueFollowup')
AddCollectorIssueFollowup = 'Add collector issue comment'
setDefaultRoles(AddCollectorIssueFollowup, ('Manager', 'Reviewer', 'Owner'))

security.declarePublic('EditCollectorIssue')
EditCollectorIssue = 'Edit collector issue'
setDefaultRoles(EditCollectorIssue, ('Manager', 'Reviewer'))

security.declarePublic('SupportIssue')
SupportIssue = 'Support collector issue'
setDefaultRoles(SupportIssue, ('Manager', 'Reviewer'))
