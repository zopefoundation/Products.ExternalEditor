## Script (Python) "folder_edit"
##parameters=title, description
##title=Edit a folder
 
context.edit( title=title,
              description=description)

qst='?portal_status_message=Folder+changed.'
 
context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_contents' + qst )

