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

subpath = traverse_subpath[0]
uid_handler = getToolByName(context, 'portal_uidhandler', None)

# appending 'isAvailable' instead of a unique id returns if
# the site permalink feature is available.
if str(subpath).strip() == 'isAvailable':
    # no permalink feature without an uid handler tool being installed
    if uid_handler is None:
        return '0'
    proptool = getToolByName(context, 'portal_properties', None)
    isAvailable = getattr(proptool, 'enable_permalink', 0)
    return str(int(isAvailable))

obj = uid_handler.getObject(subpath)

ti = obj.getTypeInfo()
method_id = ti and ti.queryMethodID('view')
if method_id:
    return getattr(obj, method_id)()
return obj()
