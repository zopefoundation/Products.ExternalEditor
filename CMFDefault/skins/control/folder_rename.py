## Script (Python) "folder_rename"
##title=Rename Object
##parameters=
REQUEST=context.REQUEST
context.manage_renameObjects(REQUEST['ids'], REQUEST['new_ids'], REQUEST)
return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Renamed.')
