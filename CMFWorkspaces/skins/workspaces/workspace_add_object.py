##parameters=type_name, RESPONSE
##title=Redirect to the form for adding the given type.

ws_url = context.absolute_url()

if not type_name:
    url = ws_url + '/workspace_view'
else:
    url = context.portal_organization.getAddFormURL(type_name, context)

RESPONSE.redirect(url)

