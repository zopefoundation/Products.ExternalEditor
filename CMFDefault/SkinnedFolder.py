##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
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
                                ( { 'name'          : 'View'
                                  , 'action'        : ''
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'name'          : 'Syndication'
                                  , 'action'        : 'synPropertiesForm'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
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

    def _index_html( self ):
        '''
            Invoke the action identified by the id "view",
            or the first action.
        '''
        tool = getToolByName( self, 'portal_types' )
        ti = tool.getTypeInfo( self )
        if ti is not None:
            path = ti.getActionById('view', None)
            if path is not None:
                view = self.restrictedTraverse(path)
                return view
            actions = ti.getActions()
            if actions:
                path = actions[0][ 'action' ]
                view = self.restrictedTraverse(path)
                return view
            raise 'Not Found', ('No default view defined for type "%s"'
                                % ti.getId())
        else:
            raise 'Not Found', ('Cannot find default view for "%s"'
                                % self.getPhysicalPath())

    security.declareProtected( CMFCorePermissions.View, 'index_html' )
    index_html = ComputedAttribute( _index_html, 1 )

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
