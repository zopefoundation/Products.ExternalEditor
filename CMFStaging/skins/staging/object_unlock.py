##parameters=REQUEST=None
##title=Unlock an object (and display the current view again)

context.portal_lock.unlock(context)
if REQUEST is not None:
    REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
