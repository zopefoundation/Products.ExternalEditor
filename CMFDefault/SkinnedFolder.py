##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Allow the "view" of a folder to be skinned by type.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _getViewFor

from DublinCore import DefaultDublinCoreImpl
from permissions import AddPortalContent
from permissions import ListFolderContents
from permissions import ManageProperties
from permissions import ModifyPortalContent
from permissions import View

factory_type_information = (
  { 'id'             : 'Skinned Folder'
  , 'meta_type'      : 'Skinned Folder'
  , 'description'    : """\
Skinned folders can define custom 'view' actions.
"""
  , 'icon'           : 'folder_icon.gif'
  , 'product'        : 'CMFDefault'
  , 'factory'        : 'addSkinnedFolder'
  , 'filter_content_types' : 0
  , 'immediate_view' : 'folder_edit_form'
  , 'aliases'        : {'(Default)': 'folder_view',
                        'view': 'folder_view'}
  , 'actions'        : ( { 'id'            : 'view'
                         , 'name'          : 'View'
                         , 'action': 'string:${object_url}/folder_view'
                         , 'permissions'   : (View,)
                         }
                       , { 'id'            : 'edit'
                         , 'name'          : 'Edit'
                         , 'action': 'string:${object_url}/folder_edit_form'
                         , 'permissions'   : (ManageProperties,)
                         }
                       , { 'id'            : 'folderContents'
                         , 'name'          : 'Folder contents'
                         , 'action': 'string:${object_url}/folder_contents'
                         , 'permissions'   : (ListFolderContents,)
                         }
                       , { 'id'            : 'new'
                         , 'name'          : 'New...'
                         , 'action': 'string:${object_url}/folder_factories'
                         , 'permissions'   : (AddPortalContent,)
                         , 'visible'       : 0
                         }
                       , { 'id'            : 'rename_items'
                         , 'name'          : 'Rename items'
                         , 'action': 'string:${object_url}/folder_rename_form'
                         , 'permissions'   : (AddPortalContent,)
                         , 'visible'       : 0
                         }
                       )
  }
,
)


class SkinnedFolder(CMFCatalogAware, PortalFolder):
    """ Skinned Folder class. 
    """
    meta_type = 'Skinned Folder'

    security = ClassSecurityInfo()

    manage_options = PortalFolder.manage_options

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return view(self, self.REQUEST)
        else:
            return view()

    security.declareProtected(View, 'view')
    view = __call__

    index_html = None  # This special value informs ZPublisher to use __call__

    # XXX: maybe we should subclass from DefaultDublinCoreImpl or refactor it

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        """ Take appropriate action after the resource has been modified.

        Update creators.
        """
        self.addCreator()

    security.declareProtected(ModifyPortalContent, 'addCreator')
    addCreator = DefaultDublinCoreImpl.addCreator.im_func

    security.declareProtected(View, 'listCreators')
    listCreators = DefaultDublinCoreImpl.listCreators.im_func

    security.declareProtected(View, 'Creator')
    Creator = DefaultDublinCoreImpl.Creator.im_func

    # We derive from CMFCatalogAware first, so we are cataloged too.

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
