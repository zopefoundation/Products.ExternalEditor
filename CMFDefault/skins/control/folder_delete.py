## Script (Python) "folder_delete"
##title=Delete objects from a folder
##parameters=
REQUEST=context.REQUEST
ret_url = context.absolute_url() + '/folder_contents'

if REQUEST.has_key( 'ids' ):
  context.manage_delObjects( REQUEST['ids'] )
  qs = '?portal_status_message=Deleted.'
  
else:
  qs = '?portal_status_message=Please+select+one+or+more+items+first.'  


return REQUEST.RESPONSE.redirect( ret_url + qs )
