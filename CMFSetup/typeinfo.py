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

import Products
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.utils import getToolByName

from permissions import ManagePortal
from utils import _xmldir
from utils import ConfiguratorBase
from utils import CONVERTER, DEFAULT, KEY


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

    ttc = TypesToolConfigurator( site, encoding )
    xml = context.readDataFile( _TOOL_FILENAME )
    if xml is None:
        return 'Types tool: Nothing to import.'

    tool_info = ttc.parseXML( xml )
    tic = TypeInfoConfigurator( site, encoding )

    for type_info in tool_info[ 'types' ]:

        filename = type_info[ 'filename' ]
        sep = filename.rfind( '/' )
        if sep == -1:
            text = context.readDataFile( filename )
        else:
            text = context.readDataFile( filename[sep+1:], filename[:sep] )
        info = tic.parseXML( text )

        for mt_info in Products.meta_types:
            if mt_info['name'] == info['kind']:
                type_info = mt_info['instance'](**info)
                break
        else:
            raise ValueError('unknown kind \'%s\'' % info['kind'])

        if info['id'] in types_tool.objectIds():
            types_tool._delObject(info['id'])

        types_tool._setObject( str( info[ 'id' ] ), type_info )


    # XXX: YAGNI?
    # importScriptsToContainer(types_tool, ('typestool_scripts',),
    #                          context)

    return 'Types tool imported.'

def exportTypesTool( context ):

    """ Export types tool content types as a set of XML files.
    """
    site = context.getSite()
    types_tool = getToolByName( site, 'portal_types' )

    ttc = TypesToolConfigurator( site ).__of__( site )
    tic = TypeInfoConfigurator( site ).__of__( site )

    tool_xml = ttc.generateXML()
    context.writeDataFile( _TOOL_FILENAME, tool_xml, 'text/xml' )

    for type_id in types_tool.listContentTypes():

        type_filename = '%s.xml' % type_id.replace( ' ', '_' )
        type_xml = tic.generateXML( type_id=type_id )
        context.writeDataFile( type_filename
                             , type_xml
                             , 'text/xml'
                             , 'types'
                             )

    # XXX: YAGNI?
    # exportScriptsFromContainer(types_tool, ('typestool_scripts',))

    return 'Types tool exported'


class TypesToolConfigurator(ConfiguratorBase):

    security = ClassSecurityInfo()

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
            info = {'id': type_id}

            if ' ' in type_id:
                info['filename'] = _getTypeFilename(type_id)

            result.append(info)

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('ticToolExport.xml', _xmldir)

    def _getImportMapping(self):

        return {
          'types-tool':
            { 'type':     {KEY: 'types', DEFAULT: (),
                           CONVERTER: self._convertTypes} },
          'type':
            { 'id':       {},
              'filename': {DEFAULT: '%(id)s'} } }

    def _convertTypes(self, val):

        for type in val:
            if type['filename'] == type['id']:
                type['filename'] = _getTypeFilename( type['filename'] )

        return val

InitializeClass(TypesToolConfigurator)


class TypeInfoConfigurator(ConfiguratorBase):

    security = ClassSecurityInfo()

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

        actions = ti.listActions()
        result['actions'] = [ ai.getMapping() for ai in actions ]

        return result

    def _getExportTemplate(self):

        return PageTemplateFile('ticTypeExport.xml', _xmldir)

    def _getImportMapping(self):

        return {
          'type-info':
            { 'id':                   {},
              'kind':                 {},
              'title':                {DEFAULT: '%(id)s'},
              'description':          {CONVERTER: self._convertToUnique},
              'meta_type':            {DEFAULT: '%(id)s'},
              'icon':                 {DEFAULT: '%(id)s.png'},
              'immediate_view':       {DEFAULT: '%(id)s_edit'},
              'global_allow':         {DEFAULT: True,
                                       CONVERTER: self._convertToBoolean},
              'filter_content_types': {DEFAULT: False,
                                       CONVERTER: self._convertToBoolean},
              'allowed_content_type': {KEY: 'allowed_content_types'},
              'allow_discussion':     {DEFAULT: False,
                                       CONVERTER: self._convertToBoolean},
              'aliases':              {CONVERTER: self._convertAliases},
              'action':               {KEY: 'actions'},
              'product':              {},
              'factory':              {},
              'constructor_path':     {},
              'permission':           {} },
          'allowed_content_type':
            { '#text':                {KEY: None} },
          'aliases':
            { 'alias':                {KEY: None} },
          'alias':
            { 'from':                 {},
              'to':                   {} },
          'action':
            { 'action_id':            {KEY: 'id'},
              'title':                {},
              'description':          {CONVERTER: self._convertToUnique},
              'category':             {},
              'condition_expr':       {KEY: 'condition'},
              'permission':           {KEY: 'permissions', DEFAULT: ()},
              'visible':              {CONVERTER: self._convertToBoolean},
              'url_expr':             {KEY: 'action'} },
          'permission':
            { '#text':                {KEY: None} } }

    def _convertAliases(self, val):

        result = {}

        for alias in val[0]:
            result[ alias['from'] ] = alias['to']

        return result

InitializeClass(TypeInfoConfigurator)


def _getTypeFilename( type_id ):

    """ Return the name of the file which holds info for a given type.
    """
    return 'types/%s.xml' % type_id.replace( ' ', '_' )
