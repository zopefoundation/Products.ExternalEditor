## Script (Python) "folder_paste"
##parameters=**kw
##title=Paste objects to a folder from the clipboard
##
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized

if context.cb_dataValid:
    try:
        result = context.manage_pasteObjects(context.REQUEST['__cp'])
        return context.setStatus( True, 'Item%s pasted.' %
                                        ( len(result) != 1 and 's' or '' ) )
    except CopyError:
        return context.setStatus(False, 'CopyError: Paste failed.')
    except zExceptions_Unauthorized:
        return context.setStatus(False, 'Unauthorized: Paste failed.')
else:
    return context.setStatus(False, 'Please copy or cut one or more items to'
                                    'paste first.')
