## Script (Python) "wiki_advanced_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=
##

context.setRegulations(d=REQUEST)

REQUEST.RESPONSE.redirect('%s' % context.wiki_page_url())


