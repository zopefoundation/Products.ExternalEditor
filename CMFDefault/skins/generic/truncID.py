## Script (Python) "truncID.py $Revision$"
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objID, size 
##title=return truncated objID
##
if len(objID) > size:
    return objID[:size] + '...'
else:
   return objID
