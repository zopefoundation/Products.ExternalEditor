## Script (Python) "addtoFavorites"
##title=Add item to favourites
##bind namespace=_
##parameters=
homeFolder=context.portal_membership.getHomeFolder()

if not hasattr(homeFolder, 'Favorites'):
  homeFolder.manage_addPortalFolder(id='Favorites', title='Favorites')
targetFolder = getattr( homeFolder, 'Favorites' )
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'Favorite', id=new_id, title=context.Title(), remote_url=myPath)
return context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/view')
