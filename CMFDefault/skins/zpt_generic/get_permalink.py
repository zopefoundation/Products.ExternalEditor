## Script (Python) "get_permalink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns the permalink url or None
##
from Products.CMFCore.utils import getToolByName

# calculate the permalink if the uid handler tool exists, permalinks
# are configured to be shown and the object is not folderish
uidtool = getToolByName(context, 'portal_uidhandler', None)
if uidtool is not None:
    proptool = getToolByName(context, 'portal_properties', None)
    showPermalink = getattr(proptool, 'enable_permalink', None)
    isFolderish = getattr(context.aq_explicit, 'isPrincipiaFolderish', None)
    
    if showPermalink and not isFolderish:
        # returns the uid (generates one if necessary)
        urltool = getToolByName(context, 'portal_url')
        uid = uidtool.register(context)
        url = "%s/permalink/%s" % (urltool(), uid)
        return url
