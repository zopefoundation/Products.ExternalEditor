## Script (Python) "searchQueryString.py $Revision$"
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=Build search query string
##
#from urllib import urlencode # no security assertions :(
import string
req=context.REQUEST
kw.update( req.form )
#return urlencode( kw )
tokens=[]
for kv in kw.items():
    tokens.append( '%s=%s' % kv )
return '?' + string.join( tokens, '&' )
