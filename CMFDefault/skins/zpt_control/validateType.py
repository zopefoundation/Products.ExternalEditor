##parameters=type_name='', **kw
##title=
##
if type_name:
    return context.setStatus(True)
else:
    return context.setStatus(False, 'Please select a content type.')
