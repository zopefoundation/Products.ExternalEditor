"""
"""

from OFS.SimpleItem import SimpleItem, Item
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile, InitializeClass
from ZPublisher.mapply import mapply

from CMFCorePermissions import ManagePortal
from utils import _dtmldir

import re, os, urllib

class MimeTypePredicate( SimpleItem ):
    """
        Predicate matching only on 'typ', using regex matching for
        string patterns (other objects conforming to 'match' can
        also be passed).
    """
    pattern         = None
    PREDICATE_TYPE  = 'mimetype'

    security = ClassSecurityInfo()

    def __init__( self, id ):
        self.id = id

    security.declareProtected( ManagePortal, 'getPatternStr' )
    def getPatternStr( self ):
        if self.pattern is None:
            return 'None'
        return self.pattern.pattern

    security.declareProtected( ManagePortal, 'manage_editForm' )
    manage_editForm = DTMLFile( 'mimetypePredEdit', _dtmldir )

    security.declareProtected( ManagePortal, 'edit' )
    def edit( self, pattern ):
        if pattern == 'None':
            pattern = None
        if type( pattern ) is type( '' ):
            pattern = re.compile( pattern )
        self.pattern = pattern

    #
    #   ContentTypeRegistryPredicate interface
    #
    security.declareObjectPublic()
    def __call__( self, name, typ, body ):
        """
            Return true if the rule matches, else false.
        """
        if self.pattern is None:
            return 0

        return self.pattern.match( typ )

    def getTypeLabel( self ):
        """
            Return a human-readable label for the predicate type.
        """
        return self.PREDICATE_TYPE

    security.declareProtected( ManagePortal, 'predicateWidget' )
    predicateWidget = DTMLFile( 'patternWidget', _dtmldir )

InitializeClass( MimeTypePredicate )

class NamePredicate( SimpleItem ):
    """
        Predicate matching only on 'name', using regex matching
        for string patterns (other objects conforming to 'match'
        and 'pattern' can also be passed).
    """
    pattern         = None
    PREDICATE_TYPE  = 'name'

    security = ClassSecurityInfo()

    def __init__( self, id ):
        self.id = id

    security.declareProtected( ManagePortal, 'getPatternStr' )
    def getPatternStr( self ):
        """
            Return a string representation of our pattern.
        """
        if self.pattern is None:
            return 'None'
        return self.pattern.pattern

    security.declareProtected( ManagePortal, 'manage_editForm' )
    manage_editForm = DTMLFile( 'namePredEdit', _dtmldir )

    security.declareProtected( ManagePortal, 'edit' )
    def edit( self, pattern ):
        if pattern == 'None':
            pattern = None
        if type( pattern ) is type( '' ):
            pattern = re.compile( pattern )
        self.pattern = pattern

    #
    #   ContentTypeRegistryPredicate interface
    #
    security.declareObjectPublic()
    def __call__( self, name, typ, body ):
        """
            Return true if the rule matches, else false.
        """
        if self.pattern is None:
            return 0
        
        return self.pattern.match( name )

    def getTypeLabel( self ):
        """
            Return a human-readable label for the predicate type.
        """
        return self.PREDICATE_TYPE

    security.declareProtected( ManagePortal, 'predicateWidget' )
    predicateWidget = DTMLFile( 'patternWidget', _dtmldir )

InitializeClass( NamePredicate )


_predicate_types = { MimeTypePredicate.PREDICATE_TYPE : MimeTypePredicate
                   , NamePredicate.PREDICATE_TYPE     : NamePredicate
                   }

def registerPredicateType( typeID, klass ):
    """
        Add a new predicate type.
    """
    _predicate_types[ typeID ] = klass


class ContentTypeRegistry( SimpleItem ):
    """
        Registry for rules which map PUT args to a CMF Type Object.
    """
    meta_type = 'Content Type Registry'
    id = 'content_type_registry'

    manage_options = ( { 'label'    : 'Predicates'
                       , 'action'   : 'manage_predicates'
                       }
                     , { 'label'    : 'Test'
                       , 'action'   : 'manage_testRegistry'
                       }
                     ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    def __init__( self ):
        self.predicate_ids  = ()
        self.predicates     = {}

    #
    #   ZMI
    #
    security.declarePublic( 'listPredicateTypes' )
    def listPredicateTypes( self ):
        """
        """
        return _predicate_types.keys()
    
    security.declareProtected( ManagePortal, 'manage_predicates' )
    manage_predicates = DTMLFile( 'registryPredList', _dtmldir )

    security.declareProtected( ManagePortal, 'doAddPredicate' )
    def doAddPredicate( self, predicate_id, predicate_type, REQUEST ):
        """
        """
        self.addPredicate( predicate_id, predicate_type )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+added.'
                              )

    security.declareProtected( ManagePortal, 'doUpdatePredicate' )
    def doUpdatePredicate( self
                         , predicate_id
                         , predicate
                         , typeObjectName
                         , REQUEST
                         ):
        """
        """
        self.updatePredicate( predicate_id, predicate, typeObjectName )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+updated.'
                              )

    security.declareProtected( ManagePortal, 'doRemovePredicate' )
    def doRemovePredicate( self, predicate_id, REQUEST ):
        """
        """
        self.removePredicate( predicate_id )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+removed.'
                              )

    security.declareProtected( ManagePortal, 'manage_testRegistry' )
    manage_testRegistry = DTMLFile( 'registryTest', _dtmldir )

    security.declareProtected( ManagePortal, 'doTestRegistry' )
    def doTestRegistry( self, name, content_type, body, REQUEST ):
        """
        """
        typeName = self.findTypeName( name, content_type, body )
        if typeName is None:
            typeName = '<unknown>'
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                               + '/manage_testRegistry'
                               + '?testResults=Type:%s'
                                       % urllib.quote( typeName )
                               )

    #
    #   Predicate manipulation
    #
    security.declarePublic( 'getPredicate' )
    def getPredicate( self, predicate_id ):
        """
            Find the predicate whose id is 'id';  return the predicate
            object, if found, or else None.
        """
        return self.predicates.get( predicate_id, ( None, None ) )[0]

    security.declarePublic( 'listPredicates' )
    def listPredicates( self ):
        """
            Return a sequence of tuples,
            '( id, ( predicate, typeObjectName ) )'
            for all predicates in the registry 
        """
        result = []
        for predicate_id in self.predicate_ids:
            result.append( ( predicate_id, self.predicates[ predicate_id ] ) )
        return tuple( result )

    security.declarePublic( 'getTypeObjectName' )
    def getTypeObjectName( self, predicate_id ):
        """
            Find the predicate whose id is 'id';  return the name of
            the type object, if found, or else None.
        """
        return self.predicates.get( predicate_id, ( None, None ) )[1]

    security.declareProtected( ManagePortal, 'addPredicate' )
    def addPredicate( self, predicate_id, predicate_type ):
        """
            Add a predicate to this element of type 'typ' to the registry.
        """
        if predicate_id in self.predicate_ids:
            raise ValueError, "Existing predicate: %s" % predicate_id

        klass = _predicate_types[ predicate_type ]
        self.predicates[ predicate_id ] = ( klass( predicate_id ), None )
        self.predicate_ids = self.predicate_ids + ( predicate_id, )

    security.declareProtected( ManagePortal, 'addPredicate' )
    def updatePredicate( self, predicate_id, predicate, typeObjectName ):
        """
            Update a predicate in this element.
        """
        if not predicate_id in self.predicate_ids:
            raise ValueError, "Unknown predicate: %s" % predicate_id

        predObj = self.predicates[ predicate_id ][0]
        mapply( predObj.edit, (), predicate.__dict__ )
        self.assignTypeName( predicate_id, typeObjectName )

    security.declareProtected( ManagePortal, 'removePredicate' )
    def removePredicate( self, predicate_id ):
        """
            Remove a predicate from the registry.
        """
        del self.predicates[ predicate_id ]
        idlist = list( self.predicate_ids )
        ndx = idlist.index( predicate_id )
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        self.predicate_ids = tuple( idlist )

    security.declareProtected( ManagePortal, 'reorderPredicate' )
    def reorderPredicate( self, predicate_id, newIndex ):
        """
            Move a given predicate to a new location in the list.
        """
        idlist = list( self.predicate_ids )
        ndx = idlist.index( predicate_id )
        pred = idlist[ ndx ]
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        idlist.insert( newIndex, pred )
        self.predicate_ids = tuple( idlist )

    security.declareProtected( ManagePortal, 'assignTypeName' )
    def assignTypeName( self, predicate_id, typeObjectName ):
        """
            Bind the given predicate to a particular type object.
        """
        pred, oldTypeObjName = self.predicates[ predicate_id ]
        self.predicates[ predicate_id ] = ( pred, typeObjectName )

    #
    #   ContentTypeRegistry interface
    #
    def findTypeName( self, name, typ, body ):
        """
            Perform a lookup over a collection of rules, returning the
            the name of the Type object corresponding to name/typ/body.
            Return None if no match found.
        """
        for predicate_id in self.predicate_ids:
            pred, typeObjectName = self.predicates[ predicate_id ]
            if pred( name, typ, body ):
                return typeObjectName

        return None

InitializeClass( ContentTypeRegistry )

def manage_addRegistry( self, REQUEST=None ):
    """
        Add a CTR to self.
    """
    CTRID = ContentTypeRegistry.id
    reg = ContentTypeRegistry()
    self._setObject( CTRID, reg )
    reg = self._getOb( CTRID )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_main'
                              + '?manage_tabs_message=Registry+added.'
                              )
