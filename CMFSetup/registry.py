""" Classes:  SetupStepRegistry

$Id$
"""
import re
from xml.sax import parseString
from xml.sax.handler import ContentHandler

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from permissions import ManagePortal
from utils import _xmldir
from utils import _getDottedName
from utils import _resolveDottedName

class SetupStepRegistry( Implicit ):

    """ Manage knowledge about steps to create / configure site.

    o Steps are composed together to define a site profile.
    """
    security = ClassSecurityInfo()

    def __init__( self ):

        self._clear()

    security.declareProtected( ManagePortal, 'listSteps' )
    def listSteps( self ):

        """ Return a sequence of IDs of registered steps.

        o Order is not significant.
        """
        return self._steps.keys()

    security.declareProtected( ManagePortal, 'sortSteps' )
    def sortSteps( self ):

        """ Return a sequence of step IDs, sorted topologically by dependency.
        """
        return self._computeTopologicalSort()

    security.declareProtected( ManagePortal, 'checkComplete' )
    def checkComplete( self ):

        """ Return a sequence of ( node, edge ) tuples for unsatisifed deps.
        """
        result = []
        seen = {}

        graph = self._computeTopologicalSort()

        for node in graph:

            dependencies = self.getStepMetadata( node )[ 'dependencies' ]

            for dependency in dependencies:

                if seen.get( dependency ) is None:
                    result.append( ( node, dependency ) )

            seen[ node ] = 1

        return result

    security.declareProtected( ManagePortal, 'getStepMetadata' )
    def getStepMetadata( self, key, default=None ):

        """ Return a mapping of metadata for the step identified by 'key'.

        o Return 'default' if no such step is registered.

        o The 'callable' metadata is available via 'getStep'.
        """
        result = {}

        info = self._steps.get( key )

        if info is None:
            return default

        for key, value in info.items():

            if key == 'callable':
                result[ key ] = _getDottedName( value )
            else:
                result[ key ] = value

        return result

    security.declareProtected( ManagePortal, 'listStepMetadata' )
    def listStepMetadata( self ):

        """ Return a sequence of mappings describing registered steps.

        o Mappings will be ordered topologically (most-dependent last).
        """
        return [ self.getStepMetadata( x ) for x in self.sortSteps() ]

    security.declareProtected( ManagePortal, 'exportAsXML' )
    def exportAsXML( self ):

        """ Return a round-trippable XML representation of the registry.

        o 'callable' values are serialized using their dotted names.
        """
        return self._exportTemplate()

    security.declarePrivate( 'getStep' )
    def getStep( self, key, default=None ):

        """ Return the callable for the step identified by 'key'.

        o Return 'default' if no such step is registered.
        """
        marker = object()
        info = self._steps.get( key, marker )

        if info is marker:
            return default

        return info[ 'callable' ]
    
    security.declarePrivate( 'registerStep' )
    def registerStep( self
                    , id
                    , version
                    , callable
                    , dependencies=()
                    , description=None
                    ):
        """ Register a setup step.

        o 'id' is a unique name for this step,

        o 'version' is a string for comparing versions, it is preferred to
          be a yyyy/mm/dd-ii formatted string (date plus two-digit
          ordinal).  when comparing two version strings, the version with
          the lower sort order is considered the older version.
          
          - Newer versions of a step supplant older ones.

          - Attempting to register an older one after a newer one results
            in a KeyError.

        o 'callable' is the setup code, which is passed a context object when
          called, and is expected to return a user-friendly message as to
          what happened.  The context object provides access to data files
          and the portal object.

        o 'dependencies' is a tuple of step ids which have to run before
          this step in order to be able to run at all. Registration of
          steps that have unmet dependencies are deferred until the
          dependencies have been registered.

        o 'description' defaults to the first line of the function doc
          string, and can be used in a display enumerating steps. If the
          docstring is also empty, the id of the step is used as a final
          fallback.
        """
        already = self.getStepMetadata( id )

        if already and already[ 'version' ] >= version:
            raise KeyError( 'Existing registration for step %s, version %s'
                          % ( id, already[ 'version' ] ) )

        info = { 'id'           : id
               , 'version'      : version
               , 'callable'     : callable
               , 'dependencies' : dependencies
               , 'description'  : description
               }

        self._steps[ id ] = info

    security.declarePrivate( 'importFromXML' )
    def importFromXML( self, text ):

        """ Parse 'text' into a clean registry.
        """
        self._clear()

        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parseString( text, _SetupStepRegistryParser( self ) )

    #
    #   Helper methods
    #
    security.declarePrivate( '_clear' )
    def _clear( self ):

        self._steps = {}

    security.declarePrivate( '_computeTopologicalSort' )
    def _computeTopologicalSort( self ):

        result = []

        graph = [ ( x[ 'id' ], x[ 'dependencies' ] )
                    for x in self._steps.values() ]

        for node, edges in graph:

            after = -1

            for edge in edges:

                if edge in result:
                    after = max( after, result.index( edge ) )

            result.insert( after + 1, node )

        return result

    security.declarePrivate( '_exportTemplate' )
    _exportTemplate = PageTemplateFile( 'ssrExport.xml', _xmldir )

InitializeClass( SetupStepRegistry )

class _SetupStepRegistryParser( ContentHandler ):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess( 'deny' )

    _WHITESPACE = re.compile( r'\s*' )

    def __init__( self, registry, encoding='latin-1' ):

        self._registry = registry
        self._encoding = encoding
        self._started = False
        self._pending = None

    def startElement( self, name, attrs ):

        if name == 'setup-steps':

            if self._started:
                raise ValueError, 'Duplicated setup-steps element: %s' % name

            self._started = True

        elif name == 'setup-step':

            if self._pending is not None:
                raise ValueError, 'Cannot nest setup-step elements'

            self._pending = dict( [ ( k, v.encode( self._encoding ) )
                                    for k, v in attrs.items() ] )

        elif name == 'dependency':

            if not self._pending:
                raise ValueError, 'Dependency outside of step'

            depended = attrs['step'].encode('latin-1')
            self._pending.setdefault( 'dependencies', [] ).append( depended )

        else:
            raise ValueError, 'Unknown element %s' % name

    def characters( self, content ):

        if self._pending is not None:
            content = content.encode( self._encoding )
            self._pending.setdefault( 'description', [] ).append( content )

    def endElement(self, name):

        if name == 'setup-steps':
            pass

        elif name == 'setup-step':

            if self._pending is None:
                raise ValueError, 'No pending step!'

            id = self._pending[ 'id' ]
            version = self._pending[ 'version' ]
            callable = _resolveDottedName( self._pending[ 'callable' ] )

            dependencies = tuple( self._pending.get( 'dependencies', () ) )
            description = ''.join( self._pending.get( 'description', [] ) )

            self._registry.registerStep( id=id
                                       , version=version
                                       , callable=callable
                                       , dependencies=dependencies
                                       , description=description
                                       )
            self._pending = None

InitializeClass( _SetupStepRegistryParser )
