## Script (Python) "file_edit"
##parameters=precondition='', file=''
##title=Edit a file
 
context.edit(
     precondition=precondition,
     file=file)

qst='?portal_status_message=File+changed.'
 
context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/file_edit_form' + qst )

