## Script (Python) "newsitem_edit_control"
##parameters=description='', text_format='', text='', change='', change_and_view='', **kw
##title=
##
form = context.REQUEST.form
if change and \
        context.validateHTML(**form) and \
        context.newsitem_edit(**form) and \
        context.setRedirect(context, 'object/edit'):
    return
elif change_and_view and \
        context.validateHTML(**form) and \
        context.newsitem_edit(**form) and \
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
