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
import os
from Globals import HTMLFile, package_home, default__class_init__
from Products.PTKBase.PortalFolder import PortalFolder


VIEW_PERMISSION                 = 'View'

ADD_TOPICS_PERMISSION           = 'Add portal topics'
CHANGE_TOPICS_PERMISSION        = 'Change portal topics'

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

addTopicForm = HTMLFile( 'topicAdd', _dtmldir, title='Add Topic' )
def addTopic( self, id, title, REQUEST=None ):
    """
        Create an empty topic.
    """
    topic = Topic(id)
    topic.id = id
    topic.title = title
    self._setObject( id, topic )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( 'manage_main' )


class Topic( PortalFolder ):
    """
    """
    meta_type='Portal Topic'

    __ac_permissions__=( ( VIEW_PERMISSION
                         , ( '', 'view', 'queryCatalog' )
                         )
                       , ( CHANGE_TOPICS_PERMISSION
                         , ( 'edit'
                           , 'editForm'
                           , 'criteriaForm'
                           , 'listCriteria'
                           , 'subtopicsForm'
                           , 'listSubtopics'
                           )
                         , ( 'Owner', 'Manager' )
                         )
                       )

    acquireCriteria = 1
    criteriaMetatypes = []

    TOPIC_ACTION = 'manage_addProduct/PortalTopic/manage_addPortalTopicForm'
    topicMetatype = ( { 'name'         : meta_type
                      , 'action'       : TOPIC_ACTION
                      , 'permission'   : ADD_TOPICS_PERMISSION
                      }
                    ,
                    )

    view = index_html = HTMLFile( 'topicView', _dtmldir )

    editForm = HTMLFile( 'topicEdit', _dtmldir )

    def all_meta_types( self ):
        return self.topicMetatype + tuple( self.criteriaMetatypes )
    
    def _criteria_metatype_ids( self ):
        result = []
        for mt in self.criteriaMetatypes:
            result.append( mt[ 'name' ] )
        return tuple( result )

    def listCriteria( self ):
        """
        """
        return self.objectValues( self._criteria_metatype_ids() )

    def listSubtopics( self ):
        """
        """
        return self.objectValues( self.meta_type )

    criteriaForm = HTMLFile( 'topicCriteria', _dtmldir )

    subtopicsForm = HTMLFile( 'topicSubtopics', _dtmldir )

    def review_state( self ):
        """
        """
        return 'Published'

    def edit( self, acquireCriteria, REQUEST=None ):
        """
        """
        self.acquireCriteria = acquireCriteria

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( '%s/view' % self.absolute_url() )
    
    def buildQuery( self ):
        """
        """
        result = {}

        if self.acquireCriteria:
            try:
                parent = self.aq_inner.aq_parent
                result.update( parent.buildQuery() )
            except:
                pass

        for criterion in self.listCriteria():
            for k, v in criterion.getCriteriaItems():
                result[ k ] = v
        
        return result
    
    def queryCatalog( self, REQUEST=None, **kw ):
        """
        """
        kw.update( self.buildQuery() )

        return apply( self.portal_catalog.searchResults
                    , ( REQUEST, ), kw )
    
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
               , { 'name'           : 'Criteria'
                 , 'url'            : url + '/criteriaForm'
                 , 'permissions'    : ( CHANGE_TOPICS_PERMISSION, )
                 , 'category'       : 'object'
                 }
               , { 'name'           : 'Subtopics'
                 , 'url'            : url + '/subtopicsForm'
                 , 'permissions'    : ( CHANGE_TOPICS_PERMISSION, )
                 , 'category'       : 'object'
                 }
               )

default__class_init__( Topic )

from Products.PTKBase.register import registerPortalContent
registerPortalContent( Topic
                     , constructors= ( addTopicForm, addTopic, )
                     , action=Topic.TOPIC_ACTION
                     , icon="images/topic.gif"
                     , productGlobals=globals()
                     )
