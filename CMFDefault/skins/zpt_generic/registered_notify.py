##parameters=member=None, password='baz', email='foo@example.org', **kw
##
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
member_id = member and member.getId() or 'foo'


options = {}

options['member_email'] = '<%s>' % email
options['email_from_name'] = ptool.getProperty('email_from_name')
options['email_from_address'] = '<%s>' % ptool.getProperty(
                                                  'email_from_address')
options['portal_title'] = ptool.title()
options['portal_description'] = ptool.getProperty('description')
options['portal_url'] = '<%s>' % portal_url
options['member_id'] = member_id
options['password'] = password
target = mtool.getActionInfo('user/logged_in')['url']
query = make_query(__ac_name=member_id, __ac_password=password)
options['login_url'] = '<%s?%s>' % (target, query)

return options
