## Script (Python) "wiki_create_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=
##

#from Products.PythonScripts.standard import special_formats

id = REQUEST.get('page')
if REQUEST.has_key('CreateFile'):
    filetype = REQUEST.get('filetype', None)
    title = REQUEST.get('title', '')
    file = REQUEST.get('file', '')
    context.create_file(id, file, filetype, title)

else:
    text = REQUEST.get('text')
    log = REQUEST.get('log')
    title = REQUEST.get('title', '')
    context.create_page(id, text, title, log)

REQUEST.RESPONSE.redirect('%s/%s' % (context.wiki_base_url(), id))
