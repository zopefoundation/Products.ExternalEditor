##parameters=b_start=0, member_id='', member_email='', password='', confirm='', send_password='', add='', cancel=''
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
        context.members_add_control(**form) and \
        context.setRedirect(rtool, 'user/join', b_start=b_start):
    return
elif cancel and \
        context.setRedirect(mtool, 'global/manage_members', b_start=b_start):
    return


options = {}

if context.REQUEST.get('portal_status_message', '') == 'Success!':
    is_anon = False
    is_newmember = True

options['title'] = is_usermanager and 'Register Member' or 'Become a Member'
options['member_id'] = member_id
options['member_email'] = member_email
options['password'] = is_newmember and context.REQUEST.get('password', '') or ''
options['send_password'] = send_password
options['portal_url'] = portal_url
options['isAnon'] = is_anon
options['isAnonOrUserManager'] = is_anon or is_usermanager
options['isNewMember'] = is_newmember
options['isOrdinaryMember'] = not (is_anon or is_newmember or is_usermanager)
options['validate_email'] = validate_email

buttons = []
if is_newmember:
    target = mtool.getActionInfo('user/logged_in')['url']
    buttons.append( {'name': 'login', 'value': 'Log in'} )
else:
    target = rtool.getActionInfo('user/join')['url']
    buttons.append( {'name': 'add', 'value': 'Register'} )
    buttons.append( {'name': 'cancel', 'value': 'Cancel'} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.join_template(**options)
