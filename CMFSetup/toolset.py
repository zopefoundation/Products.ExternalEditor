""" Ensure existence / provenance of specified tools.

$Id$
"""
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass

from permissions import ManagePortal
from utils import HandlerBase

class ToolInitializer( Implicit ):

    """ Track required / forbidden tools.
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess( 'allow' )
    
    def __init__( self, site ):

        self._site = site
        self._clear()

    #
    #   Toolset API
    #
    security.declareProtected( ManagePortal, 'listForbiddenTools' )
    def listForbiddenTools( self ):

        """ Return a list of IDs of tools which must be removed, if present.
        """
        return tuple( self._forbidden )

    security.declareProtected( ManagePortal, 'addForbiddenTool' )
    def addForbiddenTool( self, tool_id ):

        """ Add 'tool_id' to the list of forbidden tools.

        o Raise KeyError if 'tool_id' is already in the list.

        o Raise ValueError if 'tool_id' is in the "required" list.
        """
        if tool_id in self._forbidden:
            raise KeyError, 'Duplicate forbidden tool: %s' % tool_id

        if self._required.get( tool_id ) is not None:
            raise ValueError, 'Tool %s is required!' % tool_id

        self._forbidden.append( tool_id )

    security.declareProtected( ManagePortal, 'listRequiredTools' )
    def listRequiredTools( self ):

        """ Return a list of IDs of tools which must be present.
        """
        return self._required.keys()

    security.declareProtected( ManagePortal, 'getRequiredToolInfo' )
    def getRequiredToolInfo( self, tool_id ):

        """ Return a mapping describing a partiuclar required tool.

        o Keys include:

          'id' -- the ID of the tool

          'class' -- a dotted path to its class

        o Raise KeyError if 'tool_id' id not a known tool.
        """
        return self._required[ tool_id ]

    security.declareProtected( ManagePortal, 'listRequiredToolInfo' )
    def listRequiredToolInfo( self ):

        """ Return a list of IDs of tools which must be present.
        """
        return [ self.getRequiredToolInfo( x )
                        for x in self._required.keys() ]

    security.declareProtected( ManagePortal, 'addRequiredTool' )
    def addRequiredTool( self, tool_id, dotted_name ):

        """ Add a tool to our "required" list.

        o 'tool_id' is the tool's ID.

        o 'dotted_name' is a dotted (importable) name of the tool's class.

        o Raise KeyError if we have already registered a class for 'tool_id'.

        o Raise ValueError if 'tool_id' is in the "forbidden" list.
        """
        if self._required.get( tool_id ) is not None:
            raise KeyError, "Duplicate required tool: %s" % tool_id

        if tool_id in self._forbidden:
            raise ValueError, "Forbidden tool ID: %s" % tool_id

        self._required[ tool_id ] = { 'id' : tool_id
                                    , 'class' : dotted_name
                                    }

    security.declareProtected( ManagePortal, 'parseXML' )
    def parseXML( self, text, encoding=None ):

        """ Pseudo-API
        """
        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parser = _ToolsetParser( encoding )
        parseString( text, parser )

        self._clear()

        for tool_id in parser._forbidden:
            self.addForbiddenTool( tool_id )

        for tool_id, dotted_name in parser._required.items():
            self.addRequiredTool( tool_id, dotted_name )

    #
    #   Helper methods.
    #
    security.declarePrivate( '_clear' )
    def _clear( self ):

        self._forbidden = []
        self._required = {}

InitializeClass( ToolInitializer )

class _ToolsetParser( HandlerBase ):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess( 'deny' )

    def __init__( self, encoding ):

        self._encoding = encoding
        self._required = {}
        self._forbidden = []

    def startElement( self, name, attrs ):

        if name == 'tool-setup':
            pass

        elif name == 'forbidden':

            tool_id = self._extract( attrs, 'tool_id' )

            if tool_id not in self._forbidden:
                self._forbidden.append( tool_id )

        elif name == 'required':

            tool_id = self._extract( attrs, 'tool_id' )
            dotted_name = self._extract( attrs, 'class' )
            self._required[ tool_id ] = dotted_name

        else:
            raise ValueError, 'Unknown element %s' % name


InitializeClass( _ToolsetParser )
