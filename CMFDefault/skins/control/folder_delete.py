## Script (Python) "folder_delete"
##title=Delete objects from a folder
##parameters=
REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
  context.manage_delObjects(REQUEST['ids'], REQUEST)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Deleted.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Please+select+one+or+more+items+first.')
