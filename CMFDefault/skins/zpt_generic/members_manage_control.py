## Script (Python) "members_manage_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=(), b_start=0, members_new='', members_delete=''
##title=
##
from ZTUtils import Batch
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(script, 'portal_membership')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
message = ''


if members_delete:
    if ids:
        mtool.deleteMembers(ids)
        message = 'Selected member%s deleted.' % (len(ids)!=1 and 's' or '',)
    else:
        message = 'Please select one or more members to delete first.'

elif members_new:
    target = '%s/join_form' % portal_url
    context.REQUEST.RESPONSE.redirect(target)
    return None

if message:
    context.REQUEST.set('portal_status_message', message)


control = {}

target = '%s/members_manage_form' % portal_url
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
