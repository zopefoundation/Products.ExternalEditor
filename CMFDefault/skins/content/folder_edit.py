## Script (Python) "folder_edit"
##parameters=title, description, change_and_view=''
##title=Edit a folder
 
context.edit( title=title,
              description=description)

qst='portal_status_message=Folder+changed.'

if change_and_view:
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )

