## Script (Python) "folder_rename_control"
##parameters=ids=(), new_ids=(), rename='', cancel='', **kw
##title=
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import html_marshal

utool = getToolByName(script, 'portal_url')
portal_url = utool()


form = context.REQUEST.form
if rename and \
        context.folder_rename(**form) and \
        context.setRedirect(context, 'object/folderContents', **kw):
    return
elif cancel and \
        context.setRedirect(context, 'object/folderContents', **kw):
    return


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
