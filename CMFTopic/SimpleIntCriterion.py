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
    Declare simple int-match criterion class.
"""
from OFS.SimpleItem import Item
import Acquisition
from Topic import VIEW_PERMISSION
from Topic import ADD_TOPICS_PERMISSION
from Topic import CHANGE_TOPICS_PERMISSION
from Topic import _dtmldir, Topic

from Globals import HTMLFile, default__class_init__

addSimpleIntCriterionForm = HTMLFile( 'sicAdd', _dtmldir )
def addSimpleIntCriterion( self, id, value=None, direction=None, REQUEST=None ):
    """
    """
    sic = SimpleIntCriterion( id, value, direction )
    self._setObject( id, sic )
    
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( self.absolute_url() + '/folder_contents' )

SIC_ACTION = 'manage_addProduct/PortalTopic/manage_addSimpleIntCriterionForm'

class SimpleIntCriterion( Item, Acquisition.Implicit ):
    """
        Represent a simple field-match for a string value.
    """

    meta_type = 'Simple Int Criterion'

    __ac_permissions__ = ( ( VIEW_PERMISSION
                           , ( 'index_html'
                             , 'getCriteriaItems'
                             )
                           )
                         , ( CHANGE_TOPICS_PERMISSION
                           , ( 'edit', 'editForm' )
                           , ( 'Manager', 'Owner' )
                           )
                         )

    direction = None

    MINIMUM = 'min'
    MAXIMUM = 'max'
    MINMAX = 'min:max'

    def __init__( self, id, value=None, direction=None ):

        self.id = id

        if value is not None:
            self.value = int( value )
        else:
            self.value = None

        self.direction = direction
    
    #
    #   HTML interface
    #
    view = index_html = HTMLFile( 'sicView', _dtmldir )

    editForm = HTMLFile( 'sicEdit', _dtmldir )
    def edit( self, value, direction=None, REQUEST=None ):
        """
            Update the value we match against.
        """
        self.value = int( value )
        self.direction = direction

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url() + '/view' )
    
    #
    #   Criterion interface
    #
    def getCriteriaItems( self ):
        """
        """
        if self.value is None:
            return ()

        result = ( ( self.id
                   , self.value
                   )
                 ,
                 )

        if self.direction is not None:
            result = result + ( ( '%s_usage' % self.id
                                , 'range:%s' % self.direction 
                                )
                              ,
                              )
        return result

    #
    #   PTK support
    #
    listActions__roles__ = ()
    def listActions( self, info ):
        """
        """
        url = info.content_url
        return ( { 'name'           : 'View'
                 , 'url'            : url + '/view'
                 , 'permissions'    : ( VIEW_PERMISSION, )
                 , 'category'       : 'object'
                 }
               , { 'name'           : 'Edit'
                 , 'url'            : url + '/editForm'
                 , 'permissions'    : ( CHANGE_TOPICS_PERMISSION, )
                 , 'category'       : 'object'
                 }
               )

default__class_init__( SimpleIntCriterion )

Topic.criteriaMetatypes.append(
       { 'name'         : SimpleIntCriterion.meta_type
       , 'action'       : SIC_ACTION
       , 'permission'   : ADD_TOPICS_PERMISSION
       }
)

from Products.PTKBase.register import registerPortalContent
registerPortalContent( SimpleIntCriterion
                     , constructors= ( addSimpleIntCriterionForm
                                     , addSimpleIntCriterion
                                     )
                     , action=SIC_ACTION
                     , icon="images/topic.gif"
                     , productGlobals=globals()
                     )
