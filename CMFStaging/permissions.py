from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFStaging.permissions')

security.declarePublic('ManagePortal')
from Products.CMFCore.permissions import ManagePortal

security.declarePublic('ModifyPortalContent')
from Products.CMFCore.permissions import ModifyPortalContent

security.declarePublic('StageObjects')
StageObjects = 'Use version control'

security.declarePublic('UseVersionControl')
UseVersionControl = 'Use version control'

security.declarePublic('LockObjects')
LockObjects = 'WebDAV Lock items'

security.declarePublic('UnlockObjects')
UnlockObjects = 'WebDAV Unlock items'
