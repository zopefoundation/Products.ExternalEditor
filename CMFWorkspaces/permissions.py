""" CMFWorkspace product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFWorkspace.permissions')

security.declarePublic('AddPortalFolders')
from Products.CMFCore.permissions import AddPortalFolders

security.declarePublic('ManagePortal')
from Products.CMFCore.permissions import ManagePortal

security.declarePublic('View')
from Products.CMFCore.permissions import View

security.declarePublic('ManageWorkspaces')
ManageWorkspaces = 'Manage Workspaces'
