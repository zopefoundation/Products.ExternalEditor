## Script (Python) "folder_cut"
##parameters=ids, **kw
##title=Cut objects from a folder and copy to the clipboard
##
context.manage_cutObjects(ids, context.REQUEST)

return context.setStatus( True, 'Item%s cut.' %
                                ( len(ids) != 1 and 's' or '' ) )
