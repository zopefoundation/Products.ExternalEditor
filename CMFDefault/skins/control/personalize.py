## Script (Python) "personalize"
##title=Personalization Handler.
##parameters=
REQUEST=context.REQUEST
member = context.portal_membership.getAuthenticatedMember()
member.setProperties(REQUEST)

if REQUEST.has_key('portal_skin'):
    context.portal_skins.updateSkinCookie()
    
qs = '/personalize_form?portal_status_message=Member+changed.'

context.REQUEST.RESPONSE.redirect(context.portal_url() + qs)
