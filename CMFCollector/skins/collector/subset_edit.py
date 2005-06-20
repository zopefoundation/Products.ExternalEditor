##title=Update a Collector Subset
##parameters=parameters, REQUEST
##
context.clearParameters()
for parm in parameters:
    context.setParameter( parm.key, parm.value )
try:
    target = context.getActionInfo('object/edit')['url']
except AttributeError:
    # for usage with CMF < 1.5
    ti = context.getTypeInfo()
    target = "%s/%s" % ( context.absolute_url(), ti.getActionById('edit') )

REQUEST.RESPONSE.redirect('%s?portal_status_message=Updated.' % target)
