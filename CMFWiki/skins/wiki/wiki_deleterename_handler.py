## Script (Python) "wiki_deleterename_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE
##title=
##

if REQUEST.has_key('Delete'):
    if REQUEST.get('confirm-delete') != 'ON':
        raise ValueError, ("You must check the 'confirm delete'"
                           " box to commit the deletion.")
    context.delete()
    url = REQUEST.get('URL2') + '/FrontPage'
    
elif REQUEST.has_key('Rename'):
    url = context.rename(REQUEST.get('new_id'))
    
RESPONSE.redirect('%s' % url)
