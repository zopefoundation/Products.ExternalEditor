## Script (Python) "document_edit"
##parameters=text_format, text, file='', SafetyBelt=''
##title=Edit a document
 
context.edit(text_format,
             text,
             file,
             safety_belt=SafetyBelt)

qst='?portal_status_message=Document+changed.'

context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/document_edit_form' + qst )

