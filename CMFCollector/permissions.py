##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCollector product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo

try:
    from Products.CMFCore import permissions as core_permissions
except ImportError: # CMF < 1.5
    from Products.CMFCore import CMFCorePermissions as core_permissions

setDefaultRoles = core_permissions.setDefaultRoles

security = ModuleSecurityInfo('Products.CMFCollector.permissions')

security.declarePublic('View')
View = core_permissions.View

security.declarePublic('AddPortalContent')
AddPortalContent = core_permissions.AddPortalContent

security.declarePublic('AccessInactivePortalContent')
AccessInactivePortalContent = core_permissions.AccessInactivePortalContent

security.declarePublic('AccessFuturePortalContent')
AccessFuturePortalContent = core_permissions.AccessFuturePortalContent

security.declarePublic('ListFolderContents')
ListFolderContents = core_permissions.ListFolderContents

security.declarePublic('ModifyPortalContent')
ModifyPortalContent = core_permissions.ModifyPortalContent

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

del setDefaultRoles, core_permissions
