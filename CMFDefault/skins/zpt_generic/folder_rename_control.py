## Script (Python) "folder_rename_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=(), new_ids=(), rename='', cancel=''
##title=
##
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
atool = getToolByName(script, 'portal_actions')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
message = ''


if rename:
    context.manage_renameObjects(ids, new_ids)
    target = atool.getActionInfo('folder/folderContents', context)['url']
    message = 'Item%s renamed.' % ( len(ids) != 1 and 's' or '' )
    query = make_query(portal_status_message=message)
    context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
    return None

elif cancel:
    target = atool.getActionInfo('folder/folderContents', context)['url']
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

buttons = []
target = context.getActionInfo('folder/rename_items')['url']
buttons.append( {'name': 'rename', 'value': 'Rename'} )
buttons.append( {'name': 'cancel', 'value': 'Cancel'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
