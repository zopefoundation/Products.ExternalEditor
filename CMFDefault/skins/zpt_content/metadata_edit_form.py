##parameters=change='', change_and_edit='', change_and_view=''
##
form = context.REQUEST.form
if change and \
        context.metadata_edit_control(**form) and \
        context.setRedirect(context, 'object/metadata'):
    return
elif change_and_edit and \
        context.metadata_edit_control(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.metadata_edit_control(**form) and \
        context.setRedirect(context, 'object/view'):
    return


options = {}

buttons = []
target = context.getActionInfo('object/metadata')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_edit', 'value': 'Change and Edit'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.metadata_edit_template(**options)
