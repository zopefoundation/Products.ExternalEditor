## Script (Python) "expanded_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Build title which includes site title
##
site_title = context.portal_url.getPortalObject().Title()
page_title = context.Title()

if page_title != site_title:
   page_title = site_title + ": " + page_title

return page_title
