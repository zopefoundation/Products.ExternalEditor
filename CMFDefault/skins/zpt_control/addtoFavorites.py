##parameters=
##
from Products.CMFCore.utils import getToolByName

mtool = getToolByName(script, 'portal_membership')
utool = getToolByName(script, 'portal_url')

home = mtool.getHomeFolder()
if not hasattr(home, 'Favorites'):
    home.manage_addPortalFolder(id='Favorites', title='Favorites')
favorites = getattr(home, 'Favorites')

f_id = 'fav_' + str( int( context.ZopeTime() ) )
f_title = context.TitleOrId()
f_url = utool.getRelativeUrl(context)
favorites.invokeFactory('Favorite', id=f_id, title=f_title, remote_url=f_url)

context.setRedirect(context, 'object/view')
