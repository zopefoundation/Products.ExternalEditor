""" Types tool export / import

$Id$
"""
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.TypesTool import typeClasses
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import HandlerBase
from utils import _xmldir

#
#   Entry points
#
_TOOL_FILENAME = 'typestool.xml'

def importTypesTool( context ):

    """ Import types tool and content types from XML files.
    """
    site = context.getSite()
    encoding = context.getEncoding()

    types_tool = getToolByName( site, 'portal_types' )
    #if config_file is None:
    #    config_file = context.getDataFile('types.xml')

    if context.shouldPurge():

        for type in types_tool.objectIds():
            types_tool._delObject(type)

    configurator = TypeInfoConfigurator( site )
    text = context.readDataFile( _TOOL_FILENAME )

    for type_id, type_filename in configurator.parseToolXML( text ):

        text = context.readDataFile( type_filename )
        configurator.parseTypeXML( text )


    # XXX: YAGNI?
    # importScriptsToContainer(types_tool, ('typestool_scripts',),
    #                          context)

    return 'Type tool imported'

def exportTypesTool( context ):

    """ Export types tool content types as a set of XML files.
    """
    site = context.getSite()
    types_tool = getToolByName( site, 'portal_types' )
    configurator = TypeInfoConfigurator( site ).__of__( site )

    tool_xml = configurator.generateToolXML()
    context.writeDataFile( _TOOL_FILENAME, tool_xml, 'text/xml' )

    for type_id in types_tool.listContentTypes():

        type_filename = _getTypeFilename( type_id )
        type_xml = configurator.generateTypeXML( type_id )
        context.writeDataFile( type_filename, type_xml, 'text/xml' )

    # XXX: YAGNI?
    # exportScriptsFromContainer(types_tool, ('typestool_scripts',))

    return 'Types tool exported'

class TypeInfoConfigurator( Implicit ):

    security = ClassSecurityInfo()   
    security.setDefaultAccess('allow')

    def __init__( self, site ):

        self._site = site

    security.declareProtected( ManagePortal, 'getTypeInfo' )
    def getTypeInfo( self, type_id ):

        """ Return a mapping for the given type info in the site.

        o These mappings are pretty much equivalent to the stock
          'factory_type_information' elements used everywhere in the
          CMF.
        """
        typestool = getToolByName( self._site, 'portal_types' )
        try:
            ti = typestool.getTypeInfo( str( type_id ) ) # gTI expects ASCII?
        except KeyError:
            raise ValueError, 'Unknown type: %s' % type_id
        else:
            return self._makeTIMapping( ti )

    security.declareProtected( ManagePortal, 'listTypeInfo' )
    def listTypeInfo( self ):

        """ Return a list of mappings for each type info in the site.

        o These mappings are pretty much equivalent to the stock
          'factory_type_information' elements used everywhere in the
          CMF.
        """
        result = []
        typestool = getToolByName( self._site, 'portal_types' )

        type_ids = typestool.listContentTypes()

        for type_id in type_ids:
            mapping = self.getTypeInfo( type_id )
            result.append( mapping )

        return result

    security.declareProtected( ManagePortal, 'generateToolXML' )
    def generateToolXML( self ):

        """ Pseudo API.
        """
        return self._toolConfig()

    security.declareProtected( ManagePortal, 'generateTypeXML' )
    def generateTypeXML( self, type_id ):

        """ Pseudo API.
        """
        return self._typeConfig( type_id=type_id )

    security.declareProtected( ManagePortal, 'parseToolXML' )
    def parseToolXML( self, xml, encoding=None ):

        """ Pseudo API.
        """
        parser = _TypesToolParser( encoding )
        parseString( xml, parser )
        return parser._types

    security.declareProtected( ManagePortal, 'parseTypeXML' )
    def parseTypeXML( self, xml, encoding=None ):

        """ Pseudo API.
        """
        tool = getToolByName( self._site, 'portal_types' )
        parser = _TypeInfoParser( encoding )
        parseString( xml, parser )

        for info in parser._info_list:

            klass_info = [ x for x in typeClasses
                              if x[ 'name' ] == info[ 'kind' ] ][ 0 ]

            type_info = klass_info[ 'class' ]( **info )

            tool._setObject( str( info[ 'id' ] ), type_info )

    #
    #   Helper methods
    #
    security.declarePrivate( '_toolConfig' )
    _toolConfig = PageTemplateFile( 'ticToolExport.xml'
                                  , _xmldir
                                  , __name__='toolConfig'
                                  )

    security.declarePrivate( '_typeConfig' )
    _typeConfig = PageTemplateFile( 'ticTypeExport.xml'
                                  , _xmldir
                                  , __name__='typeConfig'
                                  )

    security.declarePrivate( '_makeTIMapping' )
    def _makeTIMapping( self, ti ):

        """ Convert a TypeInformation object into the appropriate mapping.
        """
        result = { 'id'                     : ti.getId()
                 , 'title'                  : ti.Title()
                 , 'description'            : ti.Description()
                 , 'meta_type'              : ti.Metatype()
                 , 'icon'                   : ti.getIcon() 
                 , 'immediate_view'         : ti.immediate_view
                 , 'global_allow'           : ti.global_allow
                 , 'filter_content_types'   : ti.filter_content_types
                 , 'allowed_content_types'  : ti.allowed_content_types
                 , 'allow_discussion'       : ti.allow_discussion
                 , 'aliases'                : ti.getMethodAliases()
                 }

        if ' ' in ti.getId():

            result[ 'filename' ]    = _getTypeFilename( ti.getId() )

        if isinstance( ti, FactoryTypeInformation ):

            result[ 'kind' ]        = FactoryTypeInformation.meta_type
            result[ 'product' ]     = ti.product
            result[ 'factory' ]     = ti.factory

        elif isinstance( ti, ScriptableTypeInformation ):

            result[ 'kind' ]             = ScriptableTypeInformation.meta_type
            result[ 'permission' ]       = ti.permission
            result[ 'constructor_path' ] = ti.constructor_path

        result[ 'actions' ] = [ self._makeActionMapping( x )
                                    for x in ti.listActions() ]

        return result

    security.declarePrivate( '_makeActionMapping' )
    def _makeActionMapping( self, ai ):

        """ Convert an ActionInformation object into a mapping.
        """
        return { 'id'             : ai.getId()
               , 'title'          : ai.Title()
               , 'description'    : ai.Description()
               , 'action'         : ai.getActionExpression()
               , 'condition'      : ai.getCondition()
               , 'permissions'    : ai.getPermissions()
               , 'category'       : ai.getCategory()
               , 'visible'        : bool( ai.getVisibility() )
               }

InitializeClass( TypeInfoConfigurator )

class _TypesToolParser( HandlerBase ):

    security = ClassSecurityInfo()

    def __init__( self, encoding ):

        self._encoding = encoding
        self._types = []

    security.declarePrivate( 'startElement' )
    def startElement( self, name, attrs ):

        if name == 'types-tool':
            pass

        if name == 'type':

            id = self._extract( attrs, 'id' )
            filename = self._extract( attrs, 'filename', id )
            
            if filename == id:
                filename = _getTypeFilename( filename )

            self._types.append( ( id, filename ) )

InitializeClass( _TypesToolParser )

_TYPE_INTS = ['global_allow', 'filter_content_types', 'allow_discussion']

class _TypeInfoParser( HandlerBase ):

    security = ClassSecurityInfo()

    def __init__( self, encoding ):

        self._encoding = encoding
        self._info_list = []
        self._description = None

    security.declarePrivate( 'startElement' )
    def startElement( self, name, attrs ):

        def _es( key, default=None ):
            return self._extract( attrs, key, default )

        def _eb( key, default=None ):
            return self._extractBoolean( attrs, key, default )

        if name == 'type-info':

            type_id                 = _es( 'id' )
            kind                    = _es( 'kind' )
            title                   = _es( 'title', type_id )
            meta_type               = _es( 'meta_type', type_id )
            icon                    = _es( 'icon', '%s.png' % type_id )
            immediate_view          = _es( 'icon', '%s_edit' % type_id )
            global_allow            = _eb( 'global_allow', True )
            filter_content_types    = _eb( 'filter_content_types', False )
            allowed_content_types   = _es( 'allowed_content_types', '' )
            allowed_content_types   = allowed_content_types.split( ',' )
            allow_discussion        = _eb( 'allow_discussion', False )

            info = { 'id'                    : type_id
                   , 'kind'                  : kind
                   , 'title'                 : title
                   , 'description'           : ''
                   , 'meta_type'             : meta_type
                   , 'icon'                  : icon
                   , 'immediate_view'        : immediate_view
                   , 'global_allow'          : global_allow
                   , 'filter_content_types'  : filter_content_types
                   , 'allowed_content_types' : allowed_content_types
                   , 'allow_discussion'      : allow_discussion
                   , 'aliases'               : {}
                   , 'actions'               : []
                   }

            if kind == FactoryTypeInformation.meta_type:

                info[ 'product' ]           = _es( 'product' )
                info[ 'factory' ]           = _es( 'factory' )

            elif kind == ScriptableTypeInformation.meta_type:

                info[ 'constructor_path' ]  = _es( 'constructor_path' )
                info[ 'permission' ]        = _es( 'permission' )

            self._info_list.append( info )

        elif name == 'aliases':
            pass

        elif name == 'alias':

            t_info = self._info_list[ -1 ]
            alias_from  = _es( 'from' )
            alias_to    = _es( 'to' )

            t_info[ 'aliases' ][ alias_from ] = alias_to

        elif name == 'action':

            t_info = self._info_list[ -1 ]
            permissions = tuple( _es( 'permissions' ).split( ',' ) )

            a_info = { 'id'             : _es( 'action_id' )
                     , 'title'          : _es( 'title' )
                     , 'name'           : _es( 'title' )
                     , 'action'         : _es( 'action_expr' )
                     , 'condition'      : _es( 'condition' )
                     , 'permissions'    : permissions
                     , 'category'       : _es( 'category' )
                     , 'visible'        : _eb( 'visible' )
                     }

            t_info[ 'actions' ].append( a_info )

        elif name == 'description':
            self._description = ''

        else:
            raise ValueError, 'Unknown element %s' % name

    security.declarePrivate('endElement')
    def endElement(self, name):

        if name == 'description':

            info = self._info_list[ -1 ]
            info[ 'description' ] = _cleanDescription( self._description )
            self._description = None

    security.declarePrivate( 'characters' )
    def characters( self, chars ):

        if self._description is not None:

            if self._encoding:
                chars = chars.encode( self._encoding )

            self._description += chars


InitializeClass( _TypeInfoParser )

def _getTypeFilename( type_id ):

    """ Return the name of the file which holds info for a given type.
    """
    return 'types/%s.xml' % type_id.replace( ' ', '_' )

def _cleanDescription( desc ):

    return ''.join( map( lambda x: x.lstrip(), desc.splitlines( 1 ) ) )
