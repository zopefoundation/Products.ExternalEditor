##title=Update a Collector Subset
##parameters=parameters, REQUEST
context.clearParameters()
for parm in parameters:
    context.setParameter( parm.key, parm.value )
info = context.getTypeInfo()
action = info.getActionById( 'edit' )
REQUEST['RESPONSE'].redirect( '%s/%s?portal_status_message=Updated.'
        % ( context.absolute_url(), action ) )
