""" CMFDefault product exceptions

$Id$
"""
from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.CMFDefault.exceptions')

security.declarePublic('AccessControl_Unauthorized')
from Products.CMFCore.exceptions import AccessControl_Unauthorized

security.declarePublic('CopyError')
from Products.CMFCore.exceptions import CopyError

security.declarePublic('EditingConflict')
from Products.CMFCore.exceptions import EditingConflict

security.declarePublic('IllegalHTML')
from Products.CMFCore.exceptions import IllegalHTML

security.declarePublic('ResourceLockedError')
from Products.CMFCore.exceptions import ResourceLockedError

security.declarePublic('zExceptions_Unauthorized')
from Products.CMFCore.exceptions import zExceptions_Unauthorized
