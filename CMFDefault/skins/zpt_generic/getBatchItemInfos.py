## Script (Python) "getBatchItemInfos"
##parameters=batch_obj
##title=
##
from Products.CMFCore.utils import getToolByName

utool = getToolByName(script, 'portal_url')
portal_url = utool()

items = []

for item in batch_obj:
    item_description = item.Description()
    item_icon = item.getIcon(1)
    item_title = item.Title()
    item_type = remote_type = item.Type()
    if item_type == 'Favorite' and not item_icon == 'p_/broken':
        item = item.getObject()
        item_description = item_description or item.Description()
        item_title = item_title or item.Title()
        remote_type = item.Type()
    is_file = remote_type in ('File', 'Image')
    is_link = remote_type == 'Link'
    items.append( { 'description': item_description,
                    'format': is_file and item.Format() or '',
                    'icon': item_icon and
                            ( '%s/%s' % (portal_url, item_icon) ) or '',
                    'size': is_file and
                            '%0.0f kb' % ( item.get_size() / 1024.0 ) or '',
                    'title': item_title,
                    'type': item_type,
                    'url': is_link and item.getRemoteUrl() or
                            item.absolute_url() } )

return tuple(items)
