## Script (Python) "join_control"
##parameters=member_id='', member_email='', password='', confirm='', send_password='', add='', cancel='', **kw
##title=
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ManageUsers

mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
rtool = getToolByName(script, 'portal_registration')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
validate_email = ptool.getProperty('validate_email')
is_anon = mtool.isAnonymousUser()
is_newmember = False
is_usermanager = mtool.checkPermission(ManageUsers, mtool)


form = context.REQUEST.form
if add and \
        context.validatePassword(**form) and \
        context.members_add(**form) and \
        context.setRedirect(rtool, 'user/join', **kw):
    return
elif cancel and \
        context.setRedirect(mtool, 'global/manage_members', **kw):
    return


control = {}

if context.REQUEST.get('portal_status_message', '') == 'Success!':
    is_anon = False
    is_newmember = True

control['title'] = is_usermanager and 'Register Member' or 'Become a Member'
control['member_id'] = member_id
control['member_email'] = member_email
control['password'] = is_newmember and context.REQUEST.get('password', '') or ''
control['send_password'] = send_password
control['portal_url'] = portal_url
control['isAnon'] = is_anon
control['isAnonOrUserManager'] = is_anon or is_usermanager
control['isNewMember'] = is_newmember
control['isOrdinaryMember'] = not (is_anon or is_newmember or is_usermanager)
control['validate_email'] = validate_email

buttons = []
if is_newmember:
    target = mtool.getActionInfo('user/logged_in')['url']
    buttons.append( {'name': 'login', 'value': 'Log in'} )
else:
    target = rtool.getActionInfo('user/join')['url']
    buttons.append( {'name': 'add', 'value': 'Register'} )
    buttons.append( {'name': 'cancel', 'value': 'Cancel'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
