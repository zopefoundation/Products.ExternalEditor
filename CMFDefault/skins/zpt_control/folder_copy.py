## Script (Python) "folder_copy"
##parameters=ids, **kw
##title=Copy objects from a folder to the clipboard
##
context.manage_copyObjects(ids, context.REQUEST)

return context.setStatus( True, 'Item%s copied.' %
                                ( len(ids) != 1 and 's' or '' ) )
