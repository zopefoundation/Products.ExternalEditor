##parameters=id='', **kw
##title=
##
if id:
    if context.checkIdAvailable(id):
        return context.setStatus(True)
    else:
        return context.setStatus(False, 'Please choose another ID.')
else:
    return context.setStatus(False, 'Please enter an ID.')
