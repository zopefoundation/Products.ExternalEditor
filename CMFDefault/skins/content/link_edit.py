## Script (Python) "link_edit"
##parameters=remote_url, change_and_view=''
##title=Edit a link
 
context.edit(remote_url=remote_url)

qst='portal_status_message=Link+changed.'

if change_and_view:
    target_action = context.getTypeInfo().getActionById( 'view' )
else:
    target_action = context.getTypeInfo().getActionById( 'edit' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
