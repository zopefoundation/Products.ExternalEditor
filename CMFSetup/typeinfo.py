##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Types tool export / import

$Id$
"""

from xml.dom.minidom import parseString as domParseString
from xml.sax import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.TypesTool import typeClasses
from Products.CMFCore.utils import getToolByName

from actions import _extractActionNodes
from permissions import ManagePortal
from utils import _coalesceTextNodeChildren
from utils import _extractDescriptionNode
from utils import _getNodeAttribute
from utils import _queryNodeAttribute
from utils import _queryNodeAttributeBoolean
from utils import _xmldir
from utils import HandlerBase

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

    for type_id, type_filename in configurator.parseToolXML(text, encoding):

        text = context.readDataFile( type_filename )
        info_list = configurator.parseTypeXML(text, encoding)

        for info in info_list:

            klass_info = [ x for x in typeClasses
                              if x[ 'name' ] == info[ 'kind' ] ][ 0 ]

            type_info = klass_info[ 'class' ]( **info )

            types_tool._setObject( str( info[ 'id' ] ), type_info )


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

        type_filename = '%s.xml' % type_id.replace( ' ', '_' )
        type_xml = configurator.generateTypeXML( type_id )
        context.writeDataFile( type_filename
                             , type_xml
                             , 'text/xml'
                             , 'types'
                             )

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
        dom = domParseString(xml)

        return _extractTypeInfoNode(dom, encoding)

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
                 , 'description'            : ti.Description().strip()
                 , 'meta_type'              : ti.Metatype()
                 , 'icon'                   : ti.getIcon()
                 , 'immediate_view'         : ti.immediate_view
                 , 'global_allow'           : bool(ti.global_allow)
                 , 'filter_content_types'   : bool(ti.filter_content_types)
                 , 'allowed_content_types'  : ti.allowed_content_types
                 , 'allow_discussion'       : bool(ti.allow_discussion)
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

        actions = ti.listActions()
        result['actions'] = [ self._makeActionMapping(ai) for ai in actions ]

        return result

    security.declarePrivate( '_makeActionMapping' )
    def _makeActionMapping( self, ai ):
        
        """ Convert a ActionInformation object into the appropriate mapping.
        """
        return  { 'id'         : ai.id
                , 'title'      : ai.title or ai.id
                , 'description': ai.description
                , 'category'   : ai.category or 'object'
                , 'condition'  : getattr(ai, 'condition', None) 
                                     and ai.condition.text or ''
                , 'permissions': ai.permissions
                , 'visible'    : bool(ai.visible)
                , 'action'     : ai.getActionExpression()
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


def _extractTypeInfoNode(parent, encoding=None):

    result = []

    ti_node = parent.getElementsByTagName('type-info')[0]

    def _es(key):
        return _getNodeAttribute(ti_node, key, encoding)

    def _qs(key, default=None):
        return _queryNodeAttribute(ti_node, key, default, encoding)

    def _qb(key, default=None):
        return _queryNodeAttributeBoolean(ti_node, key, default)

    type_id               = _es('id')
    kind                  = _es('kind')
    title                 = _qs('title', type_id)
    description           = _extractDescriptionNode(ti_node, encoding)
    meta_type             = _qs('meta_type', type_id)
    icon                  = _qs('icon', '%s.png' % type_id)
    immediate_view        = _qs('immediate_view', '%s_edit' % type_id)
    global_allow          = _qb('global_allow', True)
    filter_content_types  = _qb('filter_content_types', False)
    allowed_content_types = _extractAllowedContentTypeNodes(ti_node, encoding)
    allow_discussion      = _qb('allow_discussion', False)
    actions               = _extractActionNodes(ti_node, encoding)

    info = { 'id': type_id,
             'kind': kind,
             'title': title,
             'description': description,
             'meta_type': meta_type,
             'icon': icon,
             'immediate_view': immediate_view,
             'global_allow': global_allow,
             'filter_content_types': filter_content_types,
             'allowed_content_types': allowed_content_types,
             'allow_discussion': allow_discussion,
             'actions': actions }

    if kind == FactoryTypeInformation.meta_type:
        info['product'] = _es('product')
        info['factory'] = _es('factory')
    elif kind == ScriptableTypeInformation.meta_type:
        info['constructor_path'] = _es('constructor_path')
        info['permission'] = _es('permission')

    result.append(info)

    return result

def _extractAllowedContentTypeNodes(parent, encoding=None):

    result = []

    for act_node in parent.getElementsByTagName('allowed_content_type'):
        value = _coalesceTextNodeChildren(act_node, encoding)
        result.append(value)

    return tuple(result)

def _getTypeFilename( type_id ):

    """ Return the name of the file which holds info for a given type.
    """
    return 'types/%s.xml' % type_id.replace( ' ', '_' )
