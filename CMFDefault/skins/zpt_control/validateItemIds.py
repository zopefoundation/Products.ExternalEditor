## Script (Python) "validateItemIds"
##parameters=ids=(), **kw
##title=
##
if ids:
    return context.setStatus(True)
else:
    return context.setStatus(False, 'Please select one or more items first.')
