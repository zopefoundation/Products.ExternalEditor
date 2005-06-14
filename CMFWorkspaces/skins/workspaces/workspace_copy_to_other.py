##parameters=selected_items=(), paths=(), remove_items=0
##title=Copy or move items to the project selected by path
destination = context

if not paths:
    msg = 'No+project+selected.'
elif not selected_items:
    msg = 'No+items+selected.'
else:
    path = paths[0]
    portal = context.portal_url.getPortalObject()
    project = portal.restrictedTraverse(path)
    for id in selected_items:
        ob = context.resolve_reference(id)
        project.add_reference(ob)
        if remove_items:
            context.remove_reference(id)
    if remove_items:
        msg = 'Items+moved.'
    else:
        msg = 'Items+copied.'
    destination = project  # Visit the project now.

context.REQUEST.response.redirect(
    destination.absolute_url() + 
    "/view?portal_status_message=" + msg)
