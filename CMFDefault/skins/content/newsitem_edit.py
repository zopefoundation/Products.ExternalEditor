## Script (Python) "newsitem_edit"
##parameters=text, description, text_format=None, change_and_view=''
##title=Edit a news item
##
from Products.CMFCore.CMFCoreExceptions import CMFResourceLockedError
from Products.CMFCore.CMFCoreExceptions import IllegalHTML
from Products.CMFDefault.utils import scrubHTML
from Products.PythonScripts.standard import urlencode

try:
    text = scrubHTML( text ) # Strip Javascript, etc.
    description = scrubHTML( description )

    context.edit(text=text, description=description, text_format=text_format)
except (CMFResourceLockedError, IllegalHTML), msg:
    message = msg
    action_id = 'edit'
else:
    message = 'News Item changed.'
    if change_and_view:
        action_id = 'view'
    else:
        action_id = 'edit'

target = '%s/%s' % ( context.absolute_url(),
                     context.getTypeInfo().getActionById(action_id) )
query = urlencode( {'portal_status_message': message} )
context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
