## Script (Python) "file_edit"
##parameters=precondition='', file='', change_and_view=''
##title=Edit a file
 
context.edit(
     precondition=precondition,
     file=file)

qst='portal_status_message=File+changed.'

if change_and_view:
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
