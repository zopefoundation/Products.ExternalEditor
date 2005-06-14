from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFStaging.permissions')

security.declarePublic('ManagePortal')
security.declarePublic('ModifyPortalContent')

try:
    from Products.CMFCore.permissions import ManagePortal
    from Products.CMFCore.permissions import ModifyPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import ManagePortal
    from Products.CMFCore.CMFCorePermissions import ModifyPortalContent

security.declarePublic('StageObjects')
StageObjects = 'Use version control'

security.declarePublic('UseVersionControl')
UseVersionControl = 'Use version control'

security.declarePublic('LockObjects')
LockObjects = 'WebDAV Lock items'

security.declarePublic('UnlockObjects')
UnlockObjects = 'WebDAV Unlock items'
