## Script (Python) "document_edit_control"
##parameters=text_format='', text='', file='', SafetyBelt='', change='', change_and_view='', **kw
##title=
##
form = context.REQUEST.form
if change and \
        context.validateTextFile(**form) and \
        context.validateHTML(**form) and \
        context.document_edit(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.validateTextFile(**form) and \
        context.validateHTML(**form) and \
        context.document_edit(**form) and \
        context.setRedirect(context, 'object/view'):
    return


control = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
