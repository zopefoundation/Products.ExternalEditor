##parameters=ids, **kw
##title=Copy objects from a folder to the clipboard
##
from Products.CMFDefault.exceptions import CopyError

try:
    context.manage_copyObjects(ids, context.REQUEST)
    return context.setStatus( True, 'Item%s copied.' %
                                    ( len(ids) != 1 and 's' or '' ) )
except CopyError:
    return context.setStatus(False, 'CopyError: Copy failed.')
