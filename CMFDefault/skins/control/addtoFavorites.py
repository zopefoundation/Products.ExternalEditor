## Script (Python) "addtoFavorites"
##title=Add item to favourites
##parameters=
homeFolder=context.portal_membership.getHomeFolder()

if not hasattr(homeFolder, 'Favorites'):
  homeFolder.manage_addPortalFolder(id='Favorites', title='Favorites')
targetFolder = getattr( homeFolder, 'Favorites' )
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)
url = '%s/%s' % (context.absolute_url(), context.getTypeInfo().getActionById('view',''))
return context.REQUEST.RESPONSE.redirect(url)
