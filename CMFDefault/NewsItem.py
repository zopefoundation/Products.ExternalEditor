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
from Document import Document
from utils import parseHeadersBody

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowAction

factory_type_information = ( { 'id'             : 'News Item'
                             , 'meta_type'      : 'News Item'
                             , 'description'    : """\
News Items contain short text articles and carry a title as well as an optional description."""
                             , 'icon'           : 'newsitem_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addNewsItem'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'newsitem_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'newsitem_edit_form'
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

def addNewsItem( self
               , id
               , title=''
               , description=''
               , text=''
               , text_format='html'
               ):
    """
        Add a NewsItem
    """
    o=NewsItem( id=id
              , title=title
              , description=description
              , text=text
              , text_format=text_format
              )
    self._setObject(id, o)

class NewsItem( Document ):
    """
        A News Item
    """

    __implements__ = Document.__implements__  # redundant, but explicit

    meta_type='News Item'
    text_format = 'html'

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    def edit( self, text, description=None, text_format=None ):
        """
            Edit the News Item
        """
        if text_format is None:
            text_format = getattr(self, 'text_format', 'html')
        if description is not None:
            self.setDescription( description )
        Document.edit( self, text_format, text )


Globals.InitializeClass( NewsItem )

