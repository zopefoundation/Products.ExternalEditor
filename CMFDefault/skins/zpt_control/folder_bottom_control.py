##parameters=ids, **kw
##
subset_ids = [ obj.getId() for obj in context.listFolderContents() ]
try:
    try:
        attempt = context.moveObjectsToBottom(ids, subset_ids=subset_ids)
    except TypeError:
        # Zope 2.7.0
        attempt = context.moveObjectsToBottom(ids)
    if attempt:
        return context.setStatus( True, '%d item%s moved to bottom.' %
                                    ( attempt, (attempt != 1 and 's' or '') ) )
    else:
        return context.setStatus(False, 'Nothing to change.')
except ValueError, errmsg:
    return context.setStatus(False, 'ValueError: %s' % errmsg)
