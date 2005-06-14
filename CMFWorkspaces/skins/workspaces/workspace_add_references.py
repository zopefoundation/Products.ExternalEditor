##parameters=selected_items=(), RESPONSE=None
##title=Add listed paths to a workspace.

count = 0
for path in selected_items:
    object = context.restrictedTraverse(path)
    context.addReference(object)
    count += 1

if count == 1:
    message = "Added+1+reference."
else:
    message = "Added+%d+references." % count

if RESPONSE is not None:
    RESPONSE.redirect("%s/%s?portal_status_message=%s" %
                      (context.absolute_url(),
                       'workspace_view',
                       message))
