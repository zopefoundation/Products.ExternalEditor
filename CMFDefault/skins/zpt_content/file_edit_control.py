##parameters=file, **kw
##
from Products.CMFDefault.exceptions import ResourceLockedError

try:
    context.edit(file=file)
    return context.setStatus(True, 'File changed.')
except ResourceLockedError, errmsg:
    return context.setStatus(False, errmsg)
