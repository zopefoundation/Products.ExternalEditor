## Script (Python) "change_password"
##title=Action to change password
##parameters=password, confirm, domains=None
mt = context.portal_membership
failMessage=context.portal_registration.testPasswordValidity(password, confirm)

if failMessage:
  return context.password_form(context,
                               context.REQUEST,
                               error=failMessage)
member = mt.getAuthenticatedMember()
mt.setPassword(password, domains)
mt.credentialsChanged(password)
return context.personalize_form(context,
                                context.REQUEST,
                                portal_status_message='Password changed.')
