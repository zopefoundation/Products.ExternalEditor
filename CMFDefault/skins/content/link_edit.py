## Script (Python) "link_edit"
##parameters=remote_url
##title=Edit a link
 
context.edit(remote_url=remote_url)

qst='?portal_status_message=Link+changed.'
 
context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/link_edit_form' + qst )

