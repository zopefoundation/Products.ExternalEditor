##parameters=REQUEST=None
##title=Lock an object (and display the current view again)

context.portal_lock.lock(context)
if REQUEST is not None:
    REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
