## Script (Python) "registered_notify_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None, password='baz', email='foo@example.org', **kw
##title=
##
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
member_id = member and member.getId() or 'foo'
control = {}

control['member_email'] = '<%s>' % email
control['email_from_name'] = ptool.getProperty('email_from_name')
control['email_from_address'] = '<%s>' % ptool.getProperty(
                                                  'email_from_address')
control['portal_title'] = ptool.title()
control['portal_description'] = ptool.getProperty('description')
control['portal_url'] = '<%s>' % utool()
control['member_id'] = member_id
control['password'] = password
target = '%s/logged_in' % context.absolute_url()
query = make_query(__ac_name=member_id, __ac_password=password)
control['login_url'] = '<%s?%s>' % (target, query)

return control
