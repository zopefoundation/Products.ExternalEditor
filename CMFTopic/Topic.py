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
""" Topic: Canned catalog queries

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Globals import InitializeClass

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

from permissions import ListFolderContents
from permissions import View
from permissions import AddTopics
from permissions import ChangeTopics


# Factory type information -- makes Topic objects play nicely
# with the Types Tool (portal_types )
factory_type_information = (
  { 'id'             : 'Topic'
  , 'icon'           : 'topic_icon.gif'
  , 'meta_type'      : 'Portal Topic'
  , 'description'    : 'Topics are canned queries for organizing content '
                       'with up to date queries into the catalog.'
  , 'product'        : 'CMFTopic'
  , 'factory'        : 'addTopic'
  , 'immediate_view' : 'topic_edit_form'
  , 'allowed_content_types': ('Topic',)
  , 'aliases'        : {'(Default)': 'topic_view',
                        'view': 'topic_view'}
  , 'actions'        : ( { 'id'            : 'view'
                         , 'name'          : 'View'
                         , 'action': 'string:${object_url}/topic_view'
                         , 'permissions'   : (View,)
                         }
                       , { 'id'            : 'edit'
                         , 'name'          : 'Edit'
                         , 'action': 'string:${object_url}/topic_edit_form'
                         , 'permissions'   : (ChangeTopics,)
                         }
                       , { 'id'            : 'criteria'
                         , 'name'          : 'Criteria'
                         , 'action': 'string:${object_url}/topic_criteria_form'
                         , 'permissions'   : (ChangeTopics,)
                         }
                       , { 'id'            : 'folderContents'
                         , 'name'          : 'Subtopics'
                         , 'action': 'string:${object_url}/folder_contents'
                         , 'permissions'   : (ListFolderContents,)
                         }
                       , { 'id'            : 'new'
                         , 'name'          : 'New...'
                         , 'action': 'string:${object_url}/folder_factories'
                         , 'permissions'   : (AddTopics,)
                         , 'visible'       : 0
                         }
                       , { 'id'            : 'rename_items'
                         , 'name'          : 'Rename items'
                         , 'action': 'string:${object_url}/folder_rename_form'
                         , 'permissions'   : (AddTopics,)
                         , 'visible'       : 0
                         }
                       )
  }
,
)

def addTopic( self, id, title='', REQUEST=None ):

    """ Create an empty topic.
    """
    topic = Topic( id )
    topic.id = id
    topic.title = title
    self._setObject( id, topic )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )


class Topic( PortalFolder ):

    """ Topics are 'canned queries'
    
    o Each topic holds a set of zero or more Criteria objects specifying
      the query.
    """

    meta_type='Portal Topic'

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    acquireCriteria = 1
    _criteriaTypes = []

    security.declareProtected(ChangeTopics, 'listCriteria')
    def listCriteria( self ):

        """ Return a list of our criteria objects.
        """
        return self.objectValues( self._criteria_metatype_ids() )


    security.declareProtected(ChangeTopics, 'listCriteriaTypes')
    def listCriteriaTypes( self ):

        """ List the available criteria types.
        """
        out = []

        for ct in self._criteriaTypes:
            out.append( { 'name': ct.meta_type } )

        return out

    security.declareProtected(ChangeTopics, 'listAvailableFields')
    def listAvailableFields( self ):

        """ Return a list of available fields for new criteria.
        """
        portal_catalog = getToolByName( self, 'portal_catalog' )
        currentfields = map( lambda x: x.Field(), self.listCriteria() )
        availfields = filter(
            lambda field, cf=currentfields: field not in cf,
            portal_catalog.indexes()
            )
        return availfields

    security.declareProtected(ChangeTopics, 'listSubtopics')
    def listSubtopics( self ):

        """ Return a list of our subtopics.
        """
        return self.objectValues( self.meta_type )

    security.declareProtected(ChangeTopics, 'edit')
    def edit( self, acquireCriteria, title=None, description=None ):

        """ Set the flag which indicates whether to acquire criteria.

        o If set, reuse creiteria from parent topics;
        
        o Also update metadata about the Topic.
        """
        self.acquireCriteria = acquireCriteria
        if title is not None:
            self.title = title
        self.description = description

    security.declareProtected(View, 'buildQuery')
    def buildQuery( self ):

        """ Construct a catalog query using our criterion objects.
        """
        result = {}

        if self.acquireCriteria:

            try:
                # Tracker 290 asks to allow combinations, like this:
                # parent = aq_parent( self )
                parent = aq_parent( aq_inner( self ) )
                result.update( parent.buildQuery() )

            except: # oh well, can't find parent, or it isn't a Topic.
                pass

        for criterion in self.listCriteria():

            for key, value in criterion.getCriteriaItems():
                result[ key ] = value

        return result

    security.declareProtected(View, 'queryCatalog')
    def queryCatalog( self, REQUEST=None, **kw ):

        """ Invoke the catalog using our criteria.
        
        o Built-in criteria update any criteria passed in 'kw'.
        """
        kw.update( self.buildQuery() )
        portal_catalog = getToolByName( self, 'portal_catalog' )
        return portal_catalog.searchResults(REQUEST, **kw)

    security.declareProtected(View, 'synContentValues')
    def synContentValues( self ):

        """ Return a limited subset of the brains for our query.
        
        o Return no more brain objects than the limit set by the
          syndication tool.
        """
        syn_tool = getToolByName( self, 'portal_syndication' )
        limit = syn_tool.getMaxItems( self )
        brains = self.queryCatalog( sort_limit=limit )[ :limit ]
        return [ brain.getObject() for brain in brains ] 

    ### Criteria adding/editing/deleting
    security.declareProtected(ChangeTopics, 'addCriterion')
    def addCriterion( self, field, criterion_type ):

        """ Add a new search criterion.
        """
        crit = None
        newid = 'crit__%s' % field

        for ct in self._criteriaTypes:

            if criterion_type == ct.meta_type:
                crit = ct( newid, field )

        if crit is None:
            # No criteria type matched passed in value
            raise NameError, 'Unknown Criterion Type: %s' % criterion_type

        self._setObject( newid, crit )

    security.declareProtected(ChangeTopics, 'deleteCriterion')
    def deleteCriterion( self, criterion_id ):

        """ Delete selected criterion.
        """
        if type( criterion_id ) is type( '' ):
            self._delObject( criterion_id )
        elif type( criterion_id ) in ( type( () ), type( [] ) ):
            for cid in criterion_id:
                self._delObject( cid )

    security.declareProtected(View, 'getCriterion')
    def getCriterion( self, criterion_id ):

        """ Get the criterion object.
        """
        try:
            return self._getOb( 'crit__%s' % criterion_id )
        except AttributeError:
            return self._getOb( criterion_id )

    security.declareProtected(AddTopics, 'addSubtopic')
    def addSubtopic( self, id ):

        """ Add a new subtopic.
        """
        ti = self.getTypeInfo()
        ti.constructInstance(self, id)
        return self._getOb( id )

    #
    #   Helper methods
    #
    security.declarePrivate( '_criteria_metatype_ids' )
    def _criteria_metatype_ids( self ):

        result = []

        for mt in self._criteriaTypes:
            result.append( mt.meta_type )

        return tuple( result )

InitializeClass( Topic )
