##parameters=ids, **kw
##title=Cut objects from a folder and copy to the clipboard
##
from Products.CMFDefault.exceptions import CopyError

try:
    context.manage_cutObjects(ids, context.REQUEST)
    return context.setStatus( True, 'Item%s cut.' %
                                    ( len(ids) != 1 and 's' or '' ) )
except CopyError:
    return context.setStatus(False, 'CopyError: Cut failed.')
