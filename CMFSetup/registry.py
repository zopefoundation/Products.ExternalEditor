""" Classes:  ImportStepRegistry, ExportStepRegistry

$Id$
"""
import re
from xml.sax import parseString
from xml.sax.handler import ContentHandler

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from interfaces import IImportStepRegistry
from interfaces import IExportStepRegistry
from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir
from utils import _getDottedName
from utils import _resolveDottedName
from utils import _extractDocstring

class ImportStepRegistry( Implicit ):

    """ Manage knowledge about steps to create / configure site.

    o Steps are composed together to define a site profile.
    """
    __implements__ = ( IImportStepRegistry, )

    security = ClassSecurityInfo()

    def __init__( self ):

        self._clear()

    security.declareProtected( ManagePortal, 'listSteps' )
    def listSteps( self ):

        """ Return a sequence of IDs of registered steps.

        o Order is not significant.
        """
        return self._registered.keys()

    security.declareProtected( ManagePortal, 'sortSteps' )
    def sortSteps( self ):

        """ Return a sequence of registered step IDs
        
        o Sequence is sorted topologically by dependency, with the dependent
          steps *after* the steps they depend on.
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

        o The 'handler' metadata is available via 'getStep'.
        """
        result = {}

        info = self._registered.get( key )

        if info is None:
            return default

        return info.copy()

    security.declareProtected( ManagePortal, 'listStepMetadata' )
    def listStepMetadata( self ):

        """ Return a sequence of mappings describing registered steps.

        o Mappings will be ordered alphabetically.
        """
        step_ids = self.listSteps()
        step_ids.sort()
        return [ self.getStepMetadata( x ) for x in step_ids ]

    security.declareProtected( ManagePortal, 'generateXML' )
    def generateXML( self ):

        """ Return a round-trippable XML representation of the registry.

        o 'handler' values are serialized using their dotted names.
        """
        return self._exportTemplate()

    security.declarePrivate( 'getStep' )
    def getStep( self, key, default=None ):

        """ Return the IImportPlugin registered for 'key'.

        o Return 'default' if no such step is registered.
        """
        marker = object()
        info = self._registered.get( key, marker )

        if info is marker:
            return default

        return _resolveDottedName( info[ 'handler' ] )
    
    security.declarePrivate( 'registerStep' )
    def registerStep( self
                    , id
                    , version
                    , handler
                    , dependencies=()
                    , title=None
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

        o 'handler' should implement IImportPlugin.

        o 'dependencies' is a tuple of step ids which have to run before
          this step in order to be able to run at all. Registration of
          steps that have unmet dependencies are deferred until the
          dependencies have been registered.

        o 'title' is a one-line UI description for this step.
          If None, the first line of the documentation string of the handler
          is used, or the id if no docstring can be found.

        o 'description' is a one-line UI description for this step.
          If None, the remaining line of the documentation string of
          the handler is used, or default to ''.
        """
        already = self.getStepMetadata( id )

        if already and already[ 'version' ] >= version:
            raise KeyError( 'Existing registration for step %s, version %s'
                          % ( id, already[ 'version' ] ) )

        if title is None or description is None:

            t, d = _extractDocstring( handler, id, '' )

            title = title or t
            description = description or d

        info = { 'id'           : id
               , 'version'      : version
               , 'handler'      : _getDottedName( handler )
               , 'dependencies' : dependencies
               , 'title'        : title
               , 'description'  : description
               }

        self._registered[ id ] = info

    security.declarePrivate( 'parseXML' )
    def parseXML( self, text, encoding=None ):

        """ Parse 'text' into a clean registry.
        """
        self._clear()

        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parser = _ImportStepRegistryParser( encoding )
        parseString( text, parser )

        return parser._parsed

    #
    #   Helper methods
    #
    security.declarePrivate( '_clear' )
    def _clear( self ):

        self._registered = {}

    security.declarePrivate( '_computeTopologicalSort' )
    def _computeTopologicalSort( self ):

        result = []

        graph = [ ( x[ 'id' ], x[ 'dependencies' ] )
                    for x in self._registered.values() ]

        for node, edges in graph:

            after = -1

            for edge in edges:

                if edge in result:
                    after = max( after, result.index( edge ) )

            result.insert( after + 1, node )

        return result

    security.declarePrivate( '_exportTemplate' )
    _exportTemplate = PageTemplateFile( 'isrExport.xml', _xmldir )

InitializeClass( ImportStepRegistry )


class ExportStepRegistry( Implicit ):

    """ Registry of known site-configuration export steps.

    o Each step is registered with a unique id.
    
    o When called, with the portal object passed in as an argument,
      the step must return a sequence of three-tuples,
      ( 'data', 'content_type', 'filename' ), one for each file exported
      by the step.
      
      - 'data' is a string containing the file data;

      - 'content_type' is the MIME type of the data;

      - 'filename' is a suggested filename for use when downloading.

    """
    __implements__ = ( IExportStepRegistry, )

    security = ClassSecurityInfo()

    def __init__( self ):
 
        self._registered = {}   

    security.declareProtected( ManagePortal, 'listSteps' )
    def listSteps( self ):

        """ Return a list of registered step IDs.
        """
        return self._registered.keys()

    security.declareProtected( ManagePortal, 'getStepMetadata' )
    def getStepMetadata( self, key, default=None ):

        """ Return a mapping of metadata for the step identified by 'key'.

        o Return 'default' if no such step is registered.

        o The 'handler' metadata is available via 'getStep'.
        """
        info = self._registered.get( key )

        if info is None:
            return default

        return info.copy()

    security.declareProtected( ManagePortal, 'listStepMetadata' )
    def listStepMetadata( self ):

        """ Return a sequence of mappings describing registered steps.

        o Steps will be alphabetical by ID.
        """
        step_ids = self.listSteps()
        step_ids.sort()
        return [ self.getStepMetadata( x ) for x in step_ids ]

    security.declareProtected( ManagePortal, 'generateXML' )
    def generateXML( self ):

        """ Return a round-trippable XML representation of the registry.

        o 'handler' values are serialized using their dotted names.
        """
        return self._exportTemplate()

    security.declarePrivate( 'getStep' )
    def getStep( self, key, default=None ):

        """ Return the IExportPlugin registered for 'key'.

        o Return 'default' if no such step is registered.
        """
        marker = object()
        info = self._registered.get( key, marker )

        if info is marker:
            return default

        return _resolveDottedName( info[ 'handler' ] )

    security.declarePrivate( 'registerStep' )
    def registerStep( self, id, handler, title=None, description=None ):

        """ Register an export step.

        o 'id' is the unique identifier for this step

        o 'step' should implement IExportPlugin.

        o 'title' is a one-line UI description for this step.
          If None, the first line of the documentation string of the step
          is used, or the id if no docstring can be found.

        o 'description' is a one-line UI description for this step.
          If None, the remaining line of the documentation string of
          the step is used, or default to ''.
        """
        already = self.getStep( id )

        if already:
            raise KeyError( 'Existing registration for step %s' % id )

        if title is None or description is None:

            t, d = _extractDocstring( handler, id, '' )

            title = title or t
            description = description or d

        info = { 'id'           : id
               , 'handler'      : _getDottedName( handler )
               , 'title'        : title
               , 'description'  : description
               }

        self._registered[ id ] = info

    security.declarePrivate( 'parseXML' )
    def parseXML( self, text, encoding=None ):

        """ Parse 'text' into a clean registry.
        """
        self._clear()

        reader = getattr( text, 'read', None )

        if reader is not None:
            text = reader()

        parser = _ExportStepRegistryParser( encoding )
        parseString( text, parser )

        return parser._parsed

    #
    #   Helper methods
    #
    security.declarePrivate( '_clear' )
    def _clear( self ):

        self._registered = {}

    security.declarePrivate( '_exportTemplate' )
    _exportTemplate = PageTemplateFile( 'esrExport.xml', _xmldir )

InitializeClass( ExportStepRegistry )


class _ImportStepRegistryParser( HandlerBase ):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess( 'deny' )

    def __init__( self, encoding ):

        self._encoding = encoding
        self._started = False
        self._pending = None
        self._parsed = []

    def startElement( self, name, attrs ):

        if name == 'import-steps':

            if self._started:
                raise ValueError, 'Duplicated setup-steps element: %s' % name

            self._started = True

        elif name == 'import-step':

            if self._pending is not None:
                raise ValueError, 'Cannot nest setup-step elements'

            self._pending = dict( [ ( k, self._extract( attrs, k ) )
                                    for k in attrs.keys() ] )

            self._pending[ 'dependencies' ] = []

        elif name == 'dependency':

            if not self._pending:
                raise ValueError, 'Dependency outside of step'

            depended = self._extract( attrs, 'step' )
            self._pending[ 'dependencies' ].append( depended )

        else:
            raise ValueError, 'Unknown element %s' % name

    def characters( self, content ):

        if self._pending is not None:
            content = self._encode( content )
            self._pending.setdefault( 'description', [] ).append( content )

    def endElement(self, name):

        if name == 'import-steps':
            pass

        elif name == 'import-step':

            if self._pending is None:
                raise ValueError, 'No pending step!'

            deps = tuple( self._pending[ 'dependencies' ] )
            self._pending[ 'dependencies' ] = deps

            desc = ''.join( self._pending[ 'description' ] )
            self._pending[ 'description' ] = desc

            self._parsed.append( self._pending )
            self._pending = None

InitializeClass( _ImportStepRegistryParser )

class _ExportStepRegistryParser( HandlerBase ):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess( 'deny' )

    def __init__( self, encoding ):

        self._encoding = encoding
        self._started = False
        self._pending = None
        self._parsed = []

    def startElement( self, name, attrs ):

        if name == 'export-steps':

            if self._started:
                raise ValueError, 'Duplicated export-steps element: %s' % name

            self._started = True

        elif name == 'export-step':

            if self._pending is not None:
                raise ValueError, 'Cannot nest export-step elements'

            self._pending = dict( [ ( k, self._extract( attrs, k ) )
                                    for k in attrs.keys() ] )

        else:
            raise ValueError, 'Unknown element %s' % name

    def characters( self, content ):

        if self._pending is not None:
            content = self._encode( content )
            self._pending.setdefault( 'description', [] ).append( content )

    def endElement(self, name):

        if name == 'export-steps':
            pass

        elif name == 'export-step':

            if self._pending is None:
                raise ValueError, 'No pending step!'

            desc = ''.join( self._pending[ 'description' ] )
            self._pending[ 'description' ] = desc

            self._parsed.append( self._pending )
            self._pending = None

InitializeClass( _ExportStepRegistryParser )
