## Script (Python) "wiki_reparent_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=
##

#from Products.PythonScripts.standard import special_formats

parents = REQUEST.get('parents')
context.reparent(parents)

REQUEST.RESPONSE.redirect('%s' % context.wiki_page_url())
