## Script (Python) "folder_rename"
##parameters=ids, new_ids, **kw
##title=Rename objects in a folder
##
from Products.CMFDefault.exceptions import CopyError

if not ids == new_ids:
    try:
        context.manage_renameObjects(ids, new_ids)
        return context.setStatus(True, 'Item%s renamed.' %
                                       ( len(ids) != 1 and 's' or '' ) )
    except CopyError:
        return context.setStatus(False, 'CopyError: Rename failed.')
else:
    return context.setStatus(False, 'Nothing to change.')
