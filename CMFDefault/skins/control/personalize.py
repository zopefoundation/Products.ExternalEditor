## Script (Python) "personalize"
##title=Personalization Handler.
##bind namespace=_
##parameters=
REQUEST=context.REQUEST
context.portal_registration.setProperties(REQUEST)

if REQUEST.has_key('portal_skin'):
    context.portal_skins.updateSkinCookie()
    
qs = '/personalize_form?portal_status_message=Member+changed.'

context.REQUEST.RESPONSE.redirect(context.portal_url() + qs)
