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

ti = obj.getTypeInfo()
method_id = ti and ti.queryMethodID('view')
if method_id:
    return getattr(obj, method_id)()
return obj()
