""" CMFWorkspace product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFWorkspace.permissions')

security.declarePublic('AddPortalFolders')
try:
    from Products.CMFCore.permissions import AddPortalFolders
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalFolders

security.declarePublic('ManagePortal')
try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError:
    from Products.CMFCore.CMFCorePermissions import ManagePortal

security.declarePublic('View')
try:
    from Products.CMFCore.permissions import View
except ImportError:
    from Products.CMFCore.CMFCorePermissions import View

security.declarePublic('ManageWorkspaces')
ManageWorkspaces = 'Manage Workspaces'
