##parameters=change='', change_and_view=''
##
form = context.REQUEST.form
if change and \
        context.file_edit_control(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.file_edit_control(**form) and \
        context.setRedirect(context, 'object/view'):
    return


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.file_edit_template(**options)
