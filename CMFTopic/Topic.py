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
"""Topic: Canned catalog queries

$Id$
"""
__version__ = '$Revision$'[11:-2]

from Products.CMFTopic import TopicPermissions

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _checkPermission, _getViewFor,getToolByName
from Products.CMFCore.PortalFolder import PortalFolder

from Globals import HTMLFile, package_home, InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base
from ComputedAttribute import ComputedAttribute

import os

# Factory type information -- makes Topic objects play nicely
# with the Types Tool (portal_types )
factory_type_information = \
( { 'id'                : 'Topic'
  , 'content_icon'      : 'topic_icon.gif'
  , 'meta_type'         : 'Portal Topic'
  , 'description'       : 'Topics are canned queries for organizing content '
                          'with up to date queries into the catalog.'
  , 'product'           : 'CMFTopic'
  , 'factory'           : 'addTopic'
  , 'immediate_view'    : 'topic_edit_form'
  , 'actions'           :
    ( { 'id'            : 'view'
      , 'name'          : 'View'
      , 'action'        : 'topic_view'
      , 'permissions'   : (CMFCorePermissions.View, )
      }
    , { 'id'            : 'edit'
      , 'name'          : 'Edit'
      , 'action'        : 'topic_edit_form'
      , 'permissions'   : (TopicPermissions.ChangeTopics, )
      }
    , { 'id'            : 'criteria'
      , 'name'          : 'Criteria'
      , 'action'        : 'topic_criteria_form'
      , 'permissions'   : (TopicPermissions.ChangeTopics, )
      }
    , { 'id'            : 'subtopics'
      , 'name'          : 'Subtopics'
      , 'action'        : 'topic_subtopics_form'
      , 'permissions'   : (TopicPermissions.ChangeTopics, )
      }
    )
  }
,
)

def addTopic( self, id, title='', REQUEST=None ):
    """
        Create an empty topic.
    """
    topic = Topic( id )
    topic.id = id
    topic.title = title
    self._setObject( id, topic )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )


class Topic( PortalFolder ):
    """
        Topics are 'canned queries', which hold a set of zero or more
        Criteria objects specifying the query.
    """

    meta_type='Portal Topic'

    security = ClassSecurityInfo()

    security.declareObjectProtected( CMFCorePermissions.View )

    acquireCriteria = 1
    _criteriaTypes = []

    # Contentish interface methods
    # ----------------------------

    security.declareProtected( CMFCorePermissions.View, 'icon' )
    def icon( self ):
        """
            For the ZMI.
        """
        return self.getIcon()

    security.declarePrivate( '_verifyActionPermissions' )
    def _verifyActionPermissions( self, action ):
        pp = action.get( 'permissions', () )
        if not pp:
            return 1
        for p in pp:
            if _checkPermission( p, self ):
                return 1
        return 0

    def __call__( self ):
        """
            Invoke the default action.
        """
        view = _getViewFor( self )
        if getattr( aq_base( view ), 'isDocTemp', 0 ):
            return apply( view, ( self, self.REQUEST ) )
        else:
            return view()

    index_html = None  # This special value informs ZPublisher to use __call__

    security.declareProtected( CMFCorePermissions.View, 'view' )
    def view( self ):
        """
            Return the default view even if index_html is overridden.
        """
        return self()

    security.declarePrivate( '_criteria_metatype_ids' )
    def _criteria_metatype_ids( self ):
        result = []
        for mt in self._criteriaTypes:
            result.append( mt.meta_type )
        return tuple( result )
 
    security.declareProtected( TopicPermissions.ChangeTopics, 'listCriteria' )
    def listCriteria( self ):
        """
            Return a list of our criteria objects.
        """
        return self.objectValues( self._criteria_metatype_ids() )


    security.declareProtected( TopicPermissions.ChangeTopics
                             , 'listCriteriaTypes' )
    def listCriteriaTypes( self ):
        out = []
        for ct in self._criteriaTypes:
            out.append( {
                'name': ct.meta_type,
                } )
        return out
    
    security.declareProtected( TopicPermissions.ChangeTopics
                             , 'listAvailableFields' )
    def listAvailableFields( self ):
        """
            Return a list of available fields for new criteria.
        """
        portal_catalog = getToolByName( self, 'portal_catalog' )
        currentfields = map( lambda x: x.Field(), self.listCriteria() )
        availfields = filter(
            lambda field, cf=currentfields: field not in cf,
            portal_catalog.indexes()
            )
        return availfields

    security.declareProtected( TopicPermissions.ChangeTopics, 'listSubtopics' )
    def listSubtopics( self ):
        """
            Return a list of our subtopics.
        """
        return self.objectValues( self.meta_type )

    security.declareProtected( TopicPermissions.ChangeTopics, 'edit' )
    def edit( self, acquireCriteria, title=None, description=None ):
        """
            Set the flag which indicates whether to acquire criteria
            from parent topics; update other meta data about the Topic.
        """
        self.acquireCriteria = acquireCriteria
        if title is not None:
            self.title = title
        self.description = description
        
    security.declareProtected( CMFCorePermissions.View, 'buildQuery' )
    def buildQuery( self ):
        """
            Construct a catalog query using our criterion objects.
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
    
    security.declareProtected( CMFCorePermissions.View, 'queryCatalog' )
    def queryCatalog( self, REQUEST=None, **kw ):
        """
            Invoke the catalog using our criteria to augment any passed
            in query before calling the catalog.
        """
        kw.update( self.buildQuery() )
        portal_catalog = getToolByName( self, 'portal_catalog' )
        return apply( portal_catalog.searchResults, ( REQUEST, ), kw )


    ### Criteria adding/editing/deleting
    security.declareProtected( TopicPermissions.ChangeTopics, 'addCriterion' )
    def addCriterion( self, field, criterion_type ):
        """
            Add a new search criterion.
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

    # Backwards compatibility (deprecated)
    security.declareProtected( TopicPermissions.ChangeTopics, 'addCriteria' )
    addCriteria = addCriterion

    security.declareProtected( TopicPermissions.ChangeTopics
                             , 'deleteCriterion' )
    def deleteCriterion( self, criterion_id ):
        """
            Delete selected criterion.
        """
        if type( criterion_id ) is type( '' ):
            self._delObject( criterion_id )
        elif type( criterion_id ) in ( type( () ), type( [] ) ):
            for cid in criterion_id:
                self._delObject( cid )

    security.declarePublic( CMFCorePermissions.View, 'getCriterion' )
    def getCriterion( self, criterion_id ):
        """
            Get the criterion object.
        """
        try:
            return self._getOb( 'crit__%s' % criterion_id )
        except AttributeError:
            return self._getOb( criterion_id )

    security.declareProtected( TopicPermissions.AddTopics, 'addSubtopic' )
    def addSubtopic( self, id ):
        """
            Add a new subtopic.
        """
        try:
            tool = getToolByName( self, 'portal_types' )
        except:
            self._setOb( id, Topic( id ) )
        else:
            topictype = tool.getTypeInfo( self )
            topictype.constructInstance( self, id )

        return self._getOb( id )

# Intialize the Topic class, setting up security.
InitializeClass( Topic )
