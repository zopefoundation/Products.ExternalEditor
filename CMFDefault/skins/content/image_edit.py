## Script (Python) "image_edit"
##parameters=precondition='', file='', choice=' Change '
##title=Edit an image
 
context.edit(
     precondition=precondition,
     file=file)

qst='portal_status_message=Image+changed.'

if choice == ' Change and View ':
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
