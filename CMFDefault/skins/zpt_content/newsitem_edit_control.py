## Script (Python) "newsitem_edit_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=description='', text_format='', text='', change='', change_and_view=''
##title=
##
from ZTUtils import make_query
from Products.CMFDefault.exceptions import IllegalHTML
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import scrubHTML

message = ''


if change or change_and_view:
    ok = 1
    message = 'Nothing to change.'

    try:
        description = scrubHTML(description)
        text = scrubHTML(text)
    except IllegalHTML, msg:
        ok = 0
        message = msg

    if ok and (description != context.description
               or text_format != context.text_format or text != context.text):
        try:
            context.edit(text=text, description=description,
                         text_format=text_format)
        except ResourceLockedError, msg:
            ok = 0
            message = msg
        else:
            message = 'News Item changed.'

    if ok and change_and_view:
        target = context.getActionInfo('object/view')['url']
        query = make_query(portal_status_message=message)
        context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
        return None

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
