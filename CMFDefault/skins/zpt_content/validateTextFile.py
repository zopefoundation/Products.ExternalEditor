## Script (Python) "validateFile"
##parameters=file='', **kw
##title=
##
try:
    upload = file.read()
except AttributeError:
    return context.setStatus(True)
else:
    if upload:
        return context.setStatus(True, text=upload)
    else:
        return context.setStatus(True)
