##parameters=title, description, **kw
##
if title!=context.title or description != context.description:
    context.edit(title=title, description=description)
    return context.setStatus(True, 'Folder changed.')
else:
    return context.setStatus(False, 'Nothing to change.')
