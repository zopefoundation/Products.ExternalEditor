##parameters=change=''
##
from Products.CMFCore.utils import getToolByName

atool = getToolByName(script, 'portal_actions')
ptool = getToolByName(script, 'portal_properties')


form = context.REQUEST.form
if change and \
        context.portal_config_control(**form) and \
        context.setRedirect(atool, 'global/configPortal'):
    return


options = {}

target = atool.getActionInfo('global/configPortal')['url']
buttons = []
buttons.append( {'name': 'change', 'value': 'Change'} )
options['form'] = { 'action': target,
                    'email_from_name': ptool.getProperty('email_from_name'),
                    'email_from_address':
                                      ptool.getProperty('email_from_address'),
                    'smtp_server': ptool.smtp_server(),
                    'title': ptool.title(),
                    'description': ptool.getProperty('description'),
                    'validate_email': ptool.getProperty('validate_email'),
                    'default_charset':
                                    ptool.getProperty('default_charset', ''),
                    'listButtonInfos': tuple(buttons) }

return context.reconfig_template(**options)
