## Script (Python) "breadcrumbs.py $Revision$"
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=return breadcrumbs
##
from string import split, join, upper
from Products.PythonScripts.standard import url_quote, html_quote
portal_url = context.portal_url

path = portal_url.getRelativeUrl(context)
if not path:
    return ''

PATTERN = (
    '<a href="%(url)s">%(title)s</a>'
    )

LASTPATTERN = (
    '%(title)s'
    )

JOINER = (
    '<font color="#666666">&nbsp;&gt;&nbsp;</font>'
    )

url = portal_url()
steps = split(path,'/')
breadcrumbs = []
last = steps.pop()                      # Remove last element
last = context.Title()

# Add the home link:
breadcrumbs.append( PATTERN % { 'url'  : url,
                                'title': 'Home', } )

for step in steps:
    url = '%s/%s' % (url,url_quote(step))
    breadcrumbs.append( PATTERN % { 'url'  : url,
                                    'title': html_quote(step), } )

if last:
    breadcrumbs.append(LASTPATTERN % { 'title': html_quote(last) })

return join(breadcrumbs, JOINER)
