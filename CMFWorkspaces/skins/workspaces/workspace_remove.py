##parameters=selected_items=()
##title=Remove listed references from workspace.

message = "No items selected for removal"

if selected_items:

    missing = []
    plural = ""

    for rid in selected_items:
        try:
            context.remove_reference(rid)
        except KeyError:
            missing.append(rid)

    if missing:
        amt = len(selected_items) - len(missing)
        plural = ((amt != 1) and "s") or ""
        message = ("%s item%s removed %s targets not found"
                   % (amt, plural, len(missing)))
    else:
        amt = len(selected_items)
        plural = ((amt != 1) and "s") or ""
        message = "%s item%s removed" % (len(selected_items), plural)

container.do_next(context, message)

