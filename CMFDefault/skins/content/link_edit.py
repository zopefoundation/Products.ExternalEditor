## Script (Python) "link_edit"
##parameters=remote_url, choice=' Change '
##title=Edit a link
 
context.edit(remote_url=remote_url)

qst='portal_status_message=Link+changed.'

if choice == ' Change and View ':
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
