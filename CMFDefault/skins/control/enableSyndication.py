## Script (Python) "enableSyndication"
##title=Enable Syndication for a resource
##parameters=

if context.portal_syndication.isSiteSyndicationAllowed():
  context.portal_syndication.enableSyndication(context)
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/synPropertiesForm?portal_status_message=Syndication+Enabled')
else:
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/synPropertiesForm?portal_status_message=Syndication+Not+Allowed')

