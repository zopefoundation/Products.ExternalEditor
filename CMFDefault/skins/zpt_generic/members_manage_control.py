## Script (Python) "members_manage_control"
##parameters=ids=(), members_new='', members_delete='', **kw
##title=
##
from ZTUtils import Batch
from Products.CMFCore.utils import getToolByName

mtool = getToolByName(script, 'portal_membership')
rtool = getToolByName(script, 'portal_registration')


form = context.REQUEST.form
if members_delete and \
        context.validateMemberIds(**form) and \
        context.members_delete(**form) and \
        context.setRedirect(mtool, 'global/manage_members', **kw):
    return
elif members_new and \
        context.setRedirect(rtool, 'user/join', **kw):
    return


control = {}

target = mtool.getActionInfo('global/manage_members')['url']

b_start = kw.pop('b_start', 0)
if b_start:
    kw['b_start'] = b_start

members = mtool.listMembers()
batch_obj = Batch(members, 25, b_start, orphan=0)
items = []
for member in batch_obj:
    member_id = member.getId()
    login_time = member.getProperty('login_time')
    member_login = login_time == '2000/01/01' and '---' or login_time.Date()
    member_home = mtool.getHomeUrl(member_id, verifyPermission=0)
    items.append( {'checkbox': 'cb_%s' % member_id,
                   'email': member.getProperty('email'),
                   'login': member_login,
                   'id': member_id,
                   'home': member_home } )
navigation = context.getBatchNavigation(batch_obj, target,
                                        'member', 'members')
control['batch'] = { 'listItemInfos': tuple(items),
                     'navigation': navigation }

buttons = []
buttons.append( {'name': 'members_new', 'value': 'New...'} )
if items:
    buttons.append( {'name': 'members_delete', 'value': 'Delete'} )
control['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return control
