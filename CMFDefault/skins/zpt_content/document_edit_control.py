## Script (Python) "document_edit_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text_format='', text='', file='', SafetyBelt='', change='', change_and_view=''
##title=
##
from ZTUtils import make_query
from Products.CMFCore.CMFCoreExceptions import EditingConflict
from Products.CMFCore.CMFCoreExceptions import IllegalHTML
from Products.CMFCore.CMFCoreExceptions import ResourceLockedError
from Products.CMFDefault.utils import scrubHTML
message = ''


if change or change_and_view:
    ok = 1
    message = 'Nothing to change.'

    try:
        upload = file.read()
    except AttributeError:
        pass
    else:
        if upload:
            text = upload

    try:
        text = scrubHTML(text)
    except IllegalHTML, msg:
        ok = 0
        message = msg

    if ok and (text_format != context.text_format or text != context.text):
        try:
            context.edit(text_format, text, safety_belt=SafetyBelt)
        except (ResourceLockedError, EditingConflict), msg:
            ok = 0
            message = msg
        else:
            message = 'Document changed.'

    if ok and change_and_view:
        ti = context.getTypeInfo()
        target = ti.getActionInfo('object/view', context)['url']
        query = make_query(portal_status_message=message)
        context.REQUEST.RESPONSE.redirect( '%s?%s' % (target, query) )
        return None

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

buttons = []
ti = context.getTypeInfo()
target = ti.getActionInfo('object/edit', context)['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
