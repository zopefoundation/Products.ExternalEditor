## Script (Python) "join_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member_id='', member_email='', password='', confirm='', send_password='', add='', cancel=''
##title=
##
from Products.CMFCore.CMFCorePermissions import ManageUsers
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
rtool = getToolByName(script, 'portal_registration')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
validate_email = ptool.getProperty('validate_email')
is_anon = mtool.isAnonymousUser()
is_newmember = 0
is_usermanager = mtool.checkPermission(ManageUsers, mtool)
message = ''
valid = 1


if add:
    if validate_email:
        password = rtool.generatePassword()
    else:
        msg = rtool.testPasswordValidity(password, confirm)
        if msg:
            valid = 0
            message = msg
    if valid:
        try:
            rtool.addMember( id=member_id, password=password,
                             properties={'username':member_id,
                                         'email':member_email} )
        except ValueError, msg:
            valid = 0
            message = msg
        else:
            if validate_email or send_password:
                rtool.registeredNotify(member_id)
            if is_usermanager:
                message = 'Member registered.'
            else:
                message = 'Success!'
                is_newmember = 1
                is_anon = 0

elif cancel:
    if is_usermanager:
        target = mtool.getActionInfo('global/manage_members')['url']
    else:
        target = portal_url
    context.REQUEST.RESPONSE.redirect(target)
    return None

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

control['title'] = is_usermanager and 'Register Member' or 'Become a Member'
control['member_id'] = (not valid or is_newmember) and member_id or ''
control['member_email'] = not valid and member_email or ''
control['password'] = is_newmember and password or ''
control['send_password'] = not valid and send_password or ''
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
