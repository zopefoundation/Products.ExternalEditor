## Script (Python) "image_edit"
##parameters=precondition='', file='', change_and_view=''
##title=Edit an image
 
context.edit(
     precondition=precondition,
     file=file)

qst='portal_status_message=Image+changed.'

if change_and_view:
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
