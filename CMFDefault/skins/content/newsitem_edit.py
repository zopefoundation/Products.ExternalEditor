## Script (Python) "newsitem_edit"
##parameters=text, description
##title=Edit a news item
 
context.edit(text, description)

qst='?portal_status_message=News+Item+changed.'
 
context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/newsitem_edit_form' + qst )

