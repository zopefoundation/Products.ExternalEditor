##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals
from Globals import HTMLFile, HTML
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName
from DublinCore import DefaultDublinCoreImpl
from Link import Link

from Products.CMFCore import CMFCorePermissions

factory_type_information = ( { 'id'             : 'Favorite'
                             , 'meta_type'      : 'Favorite'
                             , 'description'    : """\
A Favorite is a Link to an intra-portal resource."""
                             , 'icon'           : 'link_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addFavorite'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'favorite_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'link_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )

def addFavorite(self, id, title='', remote_url='', description=''):
    """
    Add a Favorite
    """
    portal_url = getToolByName(self, 'portal_url')
    portal_obj = portal_url.getPortalObject()
    content_obj = portal_obj.restrictedTraverse( remote_url )
    relUrl = portal_url.getRelativeUrl( content_obj )
    o=Favorite( id, title, relUrl, description )
    self._setObject(id,o)


class Favorite( Link ):
    """
        A Favorite (special kind of Link)
    """

    __implements__ = Link.__implements__ # redundant, but explicit

    meta_type='Favorite'

    def __init__( self
                , id
                , title=''
                , remote_url=''
                , description=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.remote_url=remote_url
        self.description = description

    def getRemoteUrl(self):
        """
            returns the remote URL of the Link
        """
        portal_url = getToolByName(self, 'portal_url')
        if self.remote_url:
            return portal_url.getPortalPath() + '/' + self.remote_url
        else:
            return portal_url.getPortalPath()

    def getIcon(self, relative_to_portal=0):
        """
        Instead of a static icon, like for Link objects, we want
        to display an icon based on what the Favorite links to.
        """
        try:
            return self.getObject().getIcon(relative_to_portal)
        except:
            return 'p_/broken'

    def getObject(self):
        """
        Return the actual object that the Favorite is 
        linking to
        """
        return self.restrictedTraverse(self.getRemoteUrl())

Globals.default__class_init__(Link)

