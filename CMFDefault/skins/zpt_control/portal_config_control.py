##parameters=**kw
##
from Products.CMFCore.utils import getToolByName

ptool = getToolByName(script, 'portal_properties')

if not ptool.hasProperty('default_charset'):
    ptool.manage_addProperty('default_charset', '', 'string')
ptool.editProperties(kw)

return context.setStatus(True, 'CMF Settings changed.')
