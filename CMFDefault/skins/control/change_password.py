## Script (Python) "change_password"
##title=Action to change password
##parameters=password, confirm, domains=None

failMessage=context.portal_registration.testPasswordValidity(password, confirm)

if failMessage:
  return context.password_form(context,
                               context.REQUEST,
                               error=failMessage)

context.portal_registration.setPassword(password, domains)
context.portal_membership.credentialsChanged(password)
return context.personalize_form(context,
                                context.REQUEST,
                                portal_status_message='Password changed.')
