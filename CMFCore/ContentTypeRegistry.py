"""
"""

from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile, InitializeClass

from CMFCorePermissions import ManagePortal
from utils import _dtmldir

import re, os


class MimeTypePredicate( SimpleItem ):
    """
        Predicate matching only on 'typ', using regex matching for
        string patterns (other objects conforming to 'match' can
        also be passed).
    """
    pattern = None

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

    security.declareProtected( ManagePortal, 'patternWidget' )
    patternWidget = DTMLFile( 'patternWidget', _dtmldir
                            , predicate_type='MIMEType' )

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

InitializeClass( MimeTypePredicate )

class NamePredicate( SimpleItem ):
    """
        Predicate matching only on 'name', using regex matching
        for string patterns (other objects conforming to 'match'
        and 'pattern' can also be passed).
    """
    pattern = None

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

    security.declareProtected( ManagePortal, 'patternWidget' )
    patternWidget = DTMLFile( 'patternWidget', _dtmldir
                            , predicate_type='Name' )

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

InitializeClass( NamePredicate )


class ContentTypeRegistry( ObjectManager ):
    """
        Registry for rules which map PUT args to a CMF Type Object.
    """

    security = ClassSecurityInfo()

    def findTypeName( self, name, typ, body ):
        """
            Perform a lookup over a collection of rules, returning the
            the Type object corresponding to name/typ/body.  Return None
            if no match found.
        """

InitializeClass( ContentTypeRegistry )
