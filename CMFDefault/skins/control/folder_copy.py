## Script (Python) "folder_copy"
##title=Copy object from a folder to the clipboard
##parameters=
REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
  context.manage_copyObjects(REQUEST['ids'], REQUEST, REQUEST.RESPONSE)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Copied.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Please+select+one+or+more+items+to+copy+first.')

