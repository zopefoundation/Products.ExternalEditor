## Script (Python) "breadcrumbs.py $Revision$"
##parameters=include_root=1
##title=Return breadcrumbs
##
from Products.CMFCore.utils import getToolByName
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
result = []

if include_root:
    result.append( { 'id'      : 'root'
                   , 'title'   : ptool.title()
                   , 'url'     : portal_url
                   }
                 )

relative = utool.getRelativeContentPath(context)
portal = utool.getPortalObject()

for i in range( len( relative ) ):
    now = relative[ :i+1 ]
    obj = portal.restrictedTraverse( now )
    if not now[ -1 ] == 'talkback':
        result.append( { 'id'      : now[ -1 ]
                       , 'title'   : obj.Title()
                       , 'url'     : portal_url + '/' + '/'.join(now)
                       }
                    )

return result
