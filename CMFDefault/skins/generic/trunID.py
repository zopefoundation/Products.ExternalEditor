## Script (Python) "unauthRedirect.py $Revision$"
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objID
##title=return truncated objID
##
if len(objID) > 15:
    return objID[:15] + '...'
else:
   return objID
