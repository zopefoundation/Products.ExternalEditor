## Script (Python) "reconfig"
##title=Reconfigure Portal
##parameters=
REQUEST=context.REQUEST
context.portal_properties.editProperties(REQUEST)
return REQUEST.RESPONSE.redirect(context.portal_url() + '/reconfig_form?portal_status_message=CMF+Settings+changed.')
