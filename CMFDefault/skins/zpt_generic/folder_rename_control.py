## Script (Python) "folder_rename_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=(), new_ids=(), rename='', cancel='', **kw
##title=
##
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.utils import html_marshal

utool = getToolByName(script, 'portal_url')
portal_url = utool()
target_action = 'object/folderContents'
status = ''
message = ''


if rename:
    if not ids == new_ids:
        try:
            context.manage_renameObjects(ids, new_ids)
            status = 'success'
            message = 'Item%s renamed.' % ( len(ids) != 1 and 's' or '' )
        except CopyError:
            message = 'CopyError: Rename failed.'
    else:
        message = 'Nothing to change.'

elif cancel:
    status = 'success'


if status == 'success':
    target = context.getActionInfo(target_action)['url']
    if message:
        kw['portal_status_message'] = message
    if kw:
        query = make_query(kw)
        context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
    else:
        context.REQUEST.RESPONSE.redirect(target)
    return None

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

c = context.aq_explicit
raw_items = [ getattr(c, id) for id in ids if hasattr(c, id) ]
raw_items = [ item for item in raw_items if item.cb_isMoveable() ]
items = []
for item in raw_items:
    item_icon = item.getIcon(1)
    items.append( { 'icon': item_icon and
                            ( '%s/%s' % (portal_url, item_icon) ) or '',
                    'id': item.getId(),
                    'title': item.Title(),
                    'type': item.Type() or None } )
control['batch'] = { 'listItemInfos': tuple(items) }

target = context.getActionInfo('object/rename_items')['url']
hidden_vars = []
for name, value in html_marshal(**kw):
    hidden_vars.append( {'name': name, 'value': value} )
buttons = []
buttons.append( {'name': 'rename', 'value': 'Rename'} )
buttons.append( {'name': 'cancel', 'value': 'Cancel'} )
control['form'] = { 'action': target,
                    'listHiddenVarInfos': tuple(hidden_vars),
                    'listButtonInfos': tuple(buttons) }

return control
