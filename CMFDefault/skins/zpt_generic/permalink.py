## Script (Python) "permalink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns an object by unique id
##
from Products.CMFCore.utils import getToolByName

uid_handler = getToolByName(context, 'portal_uidhandler')
obj = uid_handler.getObject(traverse_subpath[0])
portal_type = obj.getPortalTypeName()

ptypes = getToolByName(context, 'portal_types')
method = ptypes[portal_type].getActionById('view', None)
if method:
    return getattr(obj, method)()
return obj()
