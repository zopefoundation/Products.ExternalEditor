## Script (Python) "folder_delete"
##parameters=ids, **kw
##title=Delete objects from a folder
##
context.manage_delObjects( list(ids) )

return context.setStatus( True, 'Item%s deleted.' %
                                ( len(ids) != 1 and 's' or '' ) )
