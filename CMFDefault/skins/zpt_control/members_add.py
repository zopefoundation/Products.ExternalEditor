## Script (Python) "members_add"
##parameters=member_id, password, member_email, send_password=False, **kw
##title=Add a member
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ManageUsers

mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
rtool = getToolByName(script, 'portal_registration')

try:
    rtool.addMember( id=member_id, password=password,
                     properties={'username': member_id,
                                 'email': member_email} )
except ValueError, errmsg:
    return context.setStatus(False, errmsg)
else:
    if ptool.getProperty('validate_email') or send_password:
        rtool.registeredNotify(member_id)
    if mtool.checkPermission(ManageUsers, mtool):
        return context.setStatus(True, 'Member registered.')
    else:
        return context.setStatus(False, 'Success!')
