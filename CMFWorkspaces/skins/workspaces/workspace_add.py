##parameters=type_name, RESPONSE
##title=Redirect to the form for adding the given type.

if not type_name:
    url = context.absolute_url() + '/workspace_view'
else:
    url = context.portal_organization.getAddFormURL(type_name)

RESPONSE.redirect(url)
