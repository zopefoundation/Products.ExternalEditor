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
    Allow the "view" of a folder to be skinned by type.
"""

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, Owned
from Globals import InitializeClass
from ComputedAttribute import ComputedAttribute
from Products.CMFCore.utils import _getViewFor
from Acquisition import aq_base

factory_type_information = ( { 'id'             : 'Skinned Folder'
                             , 'meta_type'      : 'Skinned Folder'
                             , 'description'    : """\
Skinned folders can define custom 'view' actions."""
                             , 'icon'           : 'folder_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addSkinnedFolder'
                             , 'filter_content_types' : 0
                             , 'immediate_view' : 'folder_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view' 
                                  , 'name'          : 'View'
                                  , 'action'        : ''
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'syndication'
                                  , 'name'          : 'Syndication'
                                  , 'action'        : 'synPropertiesForm'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'foldercontents'
                                  , 'name'          : 'Folder contents'
                                  , 'action'        : 'folder_contents'
                                  , 'permissions'   : 
                                     (CMFCorePermissions.ListFolderContents,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }
                           ,
                           )

class SkinnedFolder( PortalFolder ):
    """
    """
    meta_type = 'Skinned Folder'

    security = ClassSecurityInfo()

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
            return view()

    security.declareProtected( CMFCorePermissions.View, 'view' )
    view = __call__

    index_html = None  # This special value informs ZPublisher to use __call__

    security.declareProtected( CMFCorePermissions.View, 'Creator' )
    def Creator( self ):
        """
            Return the ID of our owner.
        """
        return self.getOwner( info=1 )[1]

InitializeClass( SkinnedFolder )

def addSkinnedFolder( self, id, title='', description='', REQUEST=None ):
    """
    """
    sf = SkinnedFolder( id, title )
    sf.description = description
    self._setObject( id, sf )
    sf = self._getOb( id )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )
