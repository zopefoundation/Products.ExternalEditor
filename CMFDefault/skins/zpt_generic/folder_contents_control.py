## Script (Python) "folder_contents_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=(), b_start=0, items_copy='', items_cut='', items_delete='', items_new='', items_paste='', items_rename='', **kw
##title=
##
from ZTUtils import Batch
from ZTUtils import make_query
from Products.CMFCore.CMFCoreExceptions import CopyError
from Products.CMFCore.CMFCoreExceptions import zExceptions_Unauthorized
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import DeleteObjects
from Products.CMFCore.CMFCorePermissions import ListFolderContents
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.utils import getToolByName
atool = getToolByName(script, 'portal_actions')
mtool = getToolByName(script, 'portal_membership')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
message = ''


if not mtool.checkPermission(ListFolderContents, context):
    ti = context.getTypeInfo()
    target = ti.getActionInfo('folder/view', context)['url']
    context.REQUEST.RESPONSE.redirect(target)
    return None


if items_copy:
    if ids:
        context.manage_copyObjects(ids, context.REQUEST)
        message = 'Item%s copied.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to copy first.'

elif items_cut:
    if ids:
        context.manage_cutObjects(ids, context.REQUEST)
        message = 'Item%s cut.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to cut first.'

elif items_delete:
    if ids:
        context.manage_delObjects( list(ids) )
        message = 'Item%s deleted.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to delete first.'

elif items_new:
    ti = context.getTypeInfo()
    target = ti.getActionInfo('folder/new', context)['url']
    context.REQUEST.RESPONSE.redirect(target)
    return None

elif items_paste:
    if context.cb_dataValid:
        try:
            result = context.manage_pasteObjects(context.REQUEST['__cp'])
            message = 'Item%s pasted.' % ( len(result) != 1 and 's' or '' )
        except CopyError:
            message = 'CopyError: Paste failed.'
        except zExceptions_Unauthorized:
            message = 'Unauthorized: Paste failed.'
    else:
        message = 'Please copy or cut one or more items to paste first.'

elif items_rename:
    if ids:
        ti = context.getTypeInfo()
        target = ti.getActionInfo('folder/rename_items', context)['url']
        query = make_query( ids=list(ids) )
        context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
        return None
    else:
        message = 'Please select one or more items to rename first.'

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

items_manage_allowed = mtool.checkPermission(ViewManagementScreens, context)
items_delete_allowed = mtool.checkPermission(DeleteObjects, context)
items_add_allowed = mtool.checkPermission(AddPortalContent, context)
upitems_list_allowed = mtool.checkPermission(ListFolderContents, context,
                                             'aq_parent')

up = {}
if upitems_list_allowed:
    up_obj = context.aq_parent
    if hasattr(up_obj, 'portal_url'):
        up_url = atool.getActionInfo('folder/folderContents', up_obj)['url']
        up = { 'icon': '%s/UpFolder_icon.gif' % portal_url,
               'id': up_obj.getId(),
               'url': up_url }
    else:
        up = { 'icon': '',
               'id': 'Root',
               'url': '' }
control['up'] = up

target = atool.getActionInfo('folder/folderContents', context)['url']
context.filterCookie()
folderfilter = context.REQUEST.get('folderfilter', '')
filter = context.decodeFolderFilter(folderfilter)
items = context.listFolderContents(contentFilter=filter)
batch_obj = Batch(items, 40, b_start, orphan=0)
items = []
for item in batch_obj:
    item_icon = item.getIcon(1)
    item_id = item.getId()
    if item.isPrincipiaFolderish:
        item_url = atool.getActionInfo('folder/folderContents', item)['url']
    else:
        ti = item.getTypeInfo()
        item_url = ti.getActionInfo('object/view', item)['url']
    items.append( { 'checkbox': items_manage_allowed and
                                ('cb_%s' % item_id) or '',
                    'icon': item_icon and
                            ( '%s/%s' % (portal_url, item_icon) ) or '',
                    'id': item_id,
                    'title': item.Title(),
                    'type': item.Type() or None,
                    'url': item_url } )
navigation = context.getBatchNavigation(batch_obj, target)
control['batch'] = { 'listItemInfos1': tuple(items[:20]),
                     'listItemInfos2': tuple(items[20:]),
                     'navigation': navigation }

buttons = []
if items_manage_allowed:
    if items_add_allowed and context.allowedContentTypes():
        buttons.append( {'name': 'items_new', 'value': 'New...'} )
        if items:
            buttons.append( {'name': 'items_rename', 'value': 'Rename'} )
    if items:
        buttons.append( {'name': 'items_cut', 'value': 'Cut'} )
        buttons.append( {'name': 'items_copy', 'value': 'Copy'} )
    if items_add_allowed and context.cb_dataValid():
        buttons.append( {'name': 'items_paste', 'value': 'Paste'} )
    if items_delete_allowed and items:
        buttons.append( {'name': 'items_delete', 'value': 'Delete'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
