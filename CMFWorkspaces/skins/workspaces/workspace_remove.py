##parameters=selected_items=(), RESPONSE=None
##title=Remove listed references from workspace.

if selected_items:

    plural = ""

    for rid in selected_items:
        context.removeReference(rid)

    amt = len(selected_items)
    plural = ((amt != 1) and "s") or ""
    message = "Removed+%s+reference%s." % (amt, plural)

if RESPONSE is not None:
    RESPONSE.redirect("%s/%s?portal_status_message=%s" %
                      (context.absolute_url(),
                       'workspace_view',
                       message))
