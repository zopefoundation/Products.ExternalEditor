## Script (Python) "newsitem_edit"
##parameters=text, description, choice=' Change '
##title=Edit a news item
 
context.edit(text, description)

qst='portal_status_message=News+Item+changed.'

if choice == ' Change and View ':
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
