## Script (Python) "folder_contents_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=b_start=0, key='', reverse=0, ids=(), delta=1, items_copy='', items_cut='', items_delete='', items_new='', items_paste='', items_rename='', items_up='', items_down='', items_top='', items_bottom='', items_sort='', **kw
##title=
##
from ZTUtils import Batch
from ZTUtils import make_query
from Products.CMFCore.CMFCoreExceptions import CopyError
from Products.CMFCore.CMFCoreExceptions import zExceptions_Unauthorized
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import DeleteObjects
from Products.CMFCore.CMFCorePermissions import ListFolderContents
from Products.CMFCore.CMFCorePermissions import ManageProperties
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import html_marshal
mtool = getToolByName(script, 'portal_membership')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
target_action = 'object/folderContents'
status = ''
message = ''
if not key:
    (key, reverse) = context.getDefaultSorting()
    is_default = 1
elif (key, reverse) == context.getDefaultSorting():
    is_default = 1
else:
    kw['key'] = key
    if reverse:
        kw['reverse'] = reverse
    is_default = 0
if b_start:
    kw['b_start'] = b_start


if not mtool.checkPermission(ListFolderContents, context):
    status = 'success'
    target_action = 'object/view'

elif items_copy:
    if ids:
        context.manage_copyObjects(ids, context.REQUEST)
        status = 'success'
        message = 'Item%s copied.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to copy first.'

elif items_cut:
    if ids:
        context.manage_cutObjects(ids, context.REQUEST)
        status = 'success'
        message = 'Item%s cut.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to cut first.'

elif items_delete:
    if ids:
        context.manage_delObjects( list(ids) )
        status = 'success'
        message = 'Item%s deleted.' % ( len(ids) != 1 and 's' or '' )
    else:
        message = 'Please select one or more items to delete first.'

elif items_new:
    status = 'success'
    target_action = 'object/new'

elif items_paste:
    if context.cb_dataValid:
        try:
            result = context.manage_pasteObjects(context.REQUEST['__cp'])
            status = 'success'
            message = 'Item%s pasted.' % ( len(result) != 1 and 's' or '' )
        except CopyError:
            message = 'CopyError: Paste failed.'
        except zExceptions_Unauthorized:
            message = 'Unauthorized: Paste failed.'
    else:
        message = 'Please copy or cut one or more items to paste first.'

elif items_rename:
    if ids:
        status = 'success'
        target_action = 'object/rename_items'
        kw['ids'] = list(ids)
    else:
        message = 'Please select one or more items to rename first.'

elif items_sort:
    context.setDefaultSorting(key, reverse)
    status = 'success'
    if kw.has_key('key'):
        del kw['key']
    if kw.has_key('reverse'):
        del kw['reverse']

elif items_up or items_down or items_top or items_bottom:
    if ids:
        subset_ids = [ obj.getId() for obj in context.listFolderContents() ]
        try:
            if items_up:
                attempt = context.moveObjectsUp(ids, delta,
                                                subset_ids=subset_ids)
                move = 'up'
            elif items_down:
                attempt = context.moveObjectsDown(ids, delta,
                                                  subset_ids=subset_ids)
                move = 'down'
            elif items_top:
                attempt = context.moveObjectsToTop(ids, subset_ids=subset_ids)
                move = 'to top'
            elif items_bottom:
                attempt = context.moveObjectsToBottom(ids,
                                                      subset_ids=subset_ids)
                move = 'to bottom'
            status = 'success'
            if attempt:
                message = '%d item%s moved %s.' % ( attempt,
                                        ( (attempt!=1) and 's' or '' ), move )
            else:
                message = 'Nothing to change.'
        except ValueError, errmsg:
            message = 'ValueError: %s' % (errmsg)
    else:
        message = 'Please select one or more items to move first.'


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

items_manage_allowed = mtool.checkPermission(ViewManagementScreens, context)
items_delete_allowed = mtool.checkPermission(DeleteObjects, context)
items_add_allowed = mtool.checkPermission(AddPortalContent, context)
upitems_list_allowed = mtool.checkPermission(ListFolderContents, context,
                                             'aq_parent')
items_move_allowed = mtool.checkPermission(ManageProperties, context)

up_info = {}
if upitems_list_allowed:
    up_obj = context.aq_parent
    if hasattr(up_obj, 'portal_url'):
        up_url = up_obj.getActionInfo('object/folderContents')['url']
        up_info = { 'icon': '%s/UpFolder_icon.gif' % portal_url,
                    'id': up_obj.getId(),
                    'url': up_url }
    else:
        up_info = { 'icon': '',
                    'id': 'Root',
                    'url': '' }
control['up_info'] = up_info

target = context.getActionInfo('object/folderContents')['url']

columns = ( {'key': 'Type',
             'title': 'Type',
             'width': '20',
             'colspan': '2'}
          , {'key': 'getId',
             'title': 'Name',
             'width': '380',
             'colspan': None}
          , {'key': 'modified',
             'title': 'Last Modified',
             'width': '160',
             'colspan': None}
          , {'key': 'position',
             'title': 'Position',
             'width': '80',
             'colspan': None }
          )
for column in columns:
    if key == column['key'] and not reverse and key != 'position':
        query = make_query(key=column['key'], reverse=1)
    else:
        query = make_query(key=column['key'])
    column['url'] = '%s?%s' % (target, query)

context.filterCookie()
folderfilter = context.REQUEST.get('folderfilter', '')
filter = context.decodeFolderFilter(folderfilter)
items = context.listFolderContents(contentFilter=filter)
items = sequence.sort( items, ((key, 'cmp', reverse and 'desc' or 'asc'),) )
batch_obj = Batch(items, 25, b_start, orphan=0)
items = []
i = 1
for item in batch_obj:
    item_icon = item.getIcon(1)
    item_id = item.getId()
    item_position = key == 'position' and str(b_start + i) or '...'
    i += 1
    item_url = item.getActionInfo( ('object/folderContents',
                                    'object/view') )['url']
    items.append( { 'checkbox': items_manage_allowed and
                                ('cb_%s' % item_id) or '',
                    'icon': item_icon and
                            ( '%s/%s' % (portal_url, item_icon) ) or '',
                    'id': item_id,
                    'modified': item.ModificationDate(),
                    'position': item_position,
                    'title': item.Title(),
                    'type': item.Type() or None,
                    'url': item_url } )
navigation = context.getBatchNavigation(batch_obj, target, **kw)
control['batch'] = { 'listColumnInfos': tuple(columns),
                     'listItemInfos': tuple(items),
                     'navigation': navigation }

hidden_vars = []
for name, value in html_marshal(**kw):
    hidden_vars.append( {'name': name, 'value': value} )
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
length = batch_obj.sequence_length
is_orderable = items_move_allowed and (key == 'position') and length > 1
is_sortable = items_move_allowed and not is_default
deltas = range( 1, min(5, length) ) + range(5, length, 5)
control['form'] = { 'action': target,
                    'listHiddenVarInfos': tuple(hidden_vars),
                    'listButtonInfos': tuple(buttons),
                    'listDeltas': tuple(deltas),
                    'is_orderable': is_orderable,
                    'is_sortable': is_sortable }

return control
