## Script (Python) "folder_paste"
##title=Paste objects to a folder from the clipboard
##parameters=
REQUEST=context.REQUEST
if context.cb_dataValid:
  context.manage_pasteObjects(REQUEST['__cp'])
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Pasted.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Copy+or+cut+one+or+more+items+to+paste+first.')
