## Script (Python) "image_edit"
##parameters=precondition='', file=''
##title=Edit an image
 
context.edit(
     precondition=precondition,
     file=file)

qst='?portal_status_message=Image+changed.'
 
context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/image_edit_form' + qst )

