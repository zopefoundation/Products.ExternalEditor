## Script (Python) "folder_top"
##parameters=ids, **kw
##title=
##
subset_ids = [ obj.getId() for obj in context.listFolderContents() ]
try:
    try:
        attempt = context.moveObjectsToTop(ids, subset_ids=subset_ids)
    except TypeError:
        # Zope 2.7.0
        attempt = context.moveObjectsToTop(ids)
    if attempt:
        return context.setStatus( True, '%d item%s moved to top.' %
                                    ( attempt, (attempt != 1 and 's' or '') ) )
    else:
        return context.setStatus(False, 'Nothing to change.')
except ValueError, errmsg:
    return context.setStatus(False, 'ValueError: %s' % errmsg)
