## Script (Python) "validateMemberIds"
##parameters=ids=(), **kw
##title=
##
if ids:
    return context.setStatus(True)
else:
    return context.setStatus(False, 'Please select one or more members first.')
