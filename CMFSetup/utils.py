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
""" CMFSetup product utilities

$Id$
"""

import os
from inspect import getdoc
from xml.dom.minidom import parseString as domParseString
from xml.sax.handler import ContentHandler

import Products
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import Implicit
from Globals import InitializeClass
from Globals import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from exceptions import BadRequest
from permissions import ManagePortal


_pkgdir = package_home( globals() )
_wwwdir = os.path.join( _pkgdir, 'www' )
_datadir = os.path.join( _pkgdir, 'data' )
_xmldir = os.path.join( _pkgdir, 'xml' )

CONVERTER, DEFAULT, KEY = range(3)


def _getDottedName( named ):

    if isinstance( named, basestring ):
        return str( named )

    try:
        return '%s.%s' % ( named.__module__, named.__name__ )
    except AttributeError:
        raise ValueError, 'Cannot compute dotted name: %s' % named

def _resolveDottedName( dotted ):

    parts = dotted.split( '.' )

    if not parts:
        raise ValueError, "incomplete dotted name: %s" % dotted

    parts_copy = parts[:]

    while parts_copy:
        try:
            module = __import__( '.'.join( parts_copy ) )
            break

        except ImportError:

            del parts_copy[ -1 ]

            if not parts_copy:
                raise

    parts = parts[ 1: ] # Funky semantics of __import__'s return value

    obj = module

    for part in parts:
        obj = getattr( obj, part )

    return obj

def _extractDocstring( func, default_title, default_description ):

    try:
        doc = getdoc( func )
        lines = doc.split( '\n' )

    except AttributeError:

        title = default_title
        description = default_description

    else:
        title = lines[ 0 ]

        if len( lines ) > 1 and lines[ 1 ].strip() == '':
            del lines[ 1 ]

        description = '\n'.join( lines[ 1: ] )

    return title, description


class HandlerBase( ContentHandler ):

    _encoding = None
    _MARKER = object()

    def _extract( self, attrs, key, default=None ):

        result = attrs.get( key, self._MARKER )

        if result is self._MARKER:
            return default

        return self._encode( result )

    def _extractBoolean( self, attrs, key, default ):

        result = attrs.get( key, self._MARKER )

        if result is self._MARKER:
            return default

        result = result.lower()
        return result in ( '1', 'yes', 'true' )

    def _encode( self, content ):

        if self._encoding is None:
            return content

        return content.encode( self._encoding )


class ConfiguratorBase(Implicit):
    """ Synthesize XML description.
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, site, encoding=None):

        self._site = site
        self._encoding = encoding
        self._template = self._getExportTemplate()

    security.declareProtected(ManagePortal, 'generateXML')
    def generateXML(self, **kw):
        """ Pseudo API.
        """
        return self._template(**kw)

    security.declareProtected(ManagePortal, 'parseXML')
    def parseXML(self, xml):
        """ Pseudo API.
        """
        reader = getattr(xml, 'read', None)

        if reader is not None:
            xml = reader()

        dom = domParseString(xml)
        root = dom.documentElement

        return self._extractNode(root)

    def _extractNode(self, node):

        nodes_map = self._getImportMapping()
        if node.nodeName not in nodes_map:
            nodes_map = self._getSharedImportMapping()
            if node.nodeName not in nodes_map:
                raise ValueError('Unknown node: %s' % node.nodeName)
        node_map = nodes_map[node.nodeName]
        info = {}

        for name, val in node.attributes.items():
            key = node_map[name].get( KEY, str(name) )
            val = self._encoding and val.encode(self._encoding) or val
            info[key] = val

        for child in node.childNodes:
            name = child.nodeName

            if not name == '#text':
                key = node_map[name].get(KEY, str(name) )
                info[key] = info.setdefault( key, () ) + (
                                                    self._extractNode(child),)

            elif '#text' in node_map:
                key = node_map['#text'].get(KEY, 'value')
                val = child.nodeValue.lstrip()
                val = self._encoding and val.encode(self._encoding) or val
                info[key] = info.setdefault(key, '') + val

        for k, v in node_map.items():
            key = v.get(KEY, k)

            if DEFAULT in v and not key in info:
                if isinstance( v[DEFAULT], basestring ):
                    info[key] = v[DEFAULT] % info
                else:
                    info[key] = v[DEFAULT]

            elif CONVERTER in v and key in info:
                info[key] = v[CONVERTER]( info[key] )

            if key is None:
                info = info[key]

        return info

    def _getSharedImportMapping(self):

        return {
          'object':
            { 'name':            {KEY: 'id'},
              'meta_type':       {},
              'property':        {KEY: 'properties', DEFAULT: ()},
              'object':          {KEY: 'objects', DEFAULT: ()} },
          'property':
            { 'name':            {KEY: 'id'},
              '#text':           {KEY: 'value', DEFAULT: ''},
              'element':         {KEY: 'elements', DEFAULT: ()},
              'type':            {},
              'select_variable': {} },
          'element':
            { 'value':           {KEY: None} },
          'description':
            { '#text':           {KEY: None} } }

    def _convertToBoolean(self, val):

        return val.lower() in ('true', 'yes', '1')

    def _convertToUnique(self, val):

        assert len(val) == 1
        return val[0]

    #
    #   generic object and property support
    #
    _o_nodes = PageTemplateFile('object_nodes.xml', _xmldir)
    _p_nodes = PageTemplateFile('property_nodes.xml', _xmldir)

    security.declareProtected(ManagePortal, 'generateObjectNodes')
    def generateObjectNodes(self, obj_infos):
        """ Pseudo API.
        """
        lines = self._o_nodes(objects=obj_infos).splitlines()
        return '\n'.join(lines)

    security.declareProtected(ManagePortal, 'generatePropertyNodes')
    def generatePropertyNodes(self, prop_infos):
        """ Pseudo API.
        """
        lines = self._p_nodes(properties=prop_infos).splitlines()
        return '\n'.join(lines)

    security.declareProtected(ManagePortal, 'initObject')
    def initObject(self, parent, o_info):

        obj_id = o_info['id']
        if obj_id not in parent.objectIds():
            meta_type = o_info['meta_type']
            for mt_info in Products.meta_types:
                if mt_info['name'] == meta_type:
                    parent._setObject( obj_id, mt_info['instance'](obj_id) )
                    break
            else:
                raise ValueError('unknown meta_type \'%s\'' % obj_id)
        obj = parent._getOb(obj_id)

        [ self.initObject(obj, info) for info in o_info['objects'] ]

        [ self.initProperty(obj, info) for info in o_info['properties'] ]

    security.declareProtected(ManagePortal, 'initProperty')
    def initProperty(self, obj, p_info):

        prop_id = p_info['id']
        prop_map = obj.propdict().get(prop_id, None)

        if prop_map is None:
            type = p_info.get('type', None)
            if type:
                val = p_info.get('select_variable', '')
                obj._setProperty(prop_id, val, type)
                prop_map = obj.propdict().get(prop_id, None)
            else:
                raise ValueError('undefined property \'%s\'' % prop_id)

        if not 'w' in prop_map.get('mode', 'wd'):
            raise BadRequest('%s cannot be changed' % prop_id)

        if prop_map.get('type') == 'multiple selection':
            prop_value = p_info['elements'] or ()
        else:
            # if we pass a *string* to _updateProperty, all other values
            # are converted to the right type
            prop_value = p_info['elements'] or str( p_info['value'] )

        obj._updateProperty(prop_id, prop_value)

    def _extractObject(self, obj):

        properties = []
        subobjects = []

        if getattr( aq_base(obj), '_propertyMap' ):
            for prop_map in obj._propertyMap():
                properties.append( self._extractProperty(obj, prop_map) )

        if getattr( aq_base(obj), 'objectValues' ):
            for sub in obj.objectValues():
                subobjects.append( self._extractObject(sub) )

        return { 'id': obj.getId(),
                 'meta_type': obj.meta_type,
                 'properties': tuple(properties),
                 'subobjects': tuple(subobjects) }

    def _extractProperty(self, obj, prop_map):

        prop_id = prop_map['id']
        prop = obj.getProperty(prop_id)

        if isinstance(prop, tuple):
            prop_value = ''
            prop_elements = prop
        else:
            prop_value = prop
            prop_elements = ()

        if 'd' in prop_map.get('mode', 'wd') and not prop_id == 'title':
            type = prop_map.get('type', 'string')
            select_variable = prop_map.get('select_variable', None)
        else:
            type = None
            select_variable = None

        return { 'id': prop_id,
                 'value': prop_value,
                 'elements': prop_elements,
                 'type': type,
                 'select_variable': select_variable }

InitializeClass(ConfiguratorBase)


#
#   deprecated DOM parsing utilities
#
_marker = object()

def _queryNodeAttribute( node, attr_name, default, encoding=None ):

    """ Extract a string-valued attribute from node.

    o Return 'default' if the attribute is not present.
    """
    attr_node = node.attributes.get( attr_name, _marker )

    if attr_node is _marker:
        return default

    value = attr_node.nodeValue

    if encoding is not None:
        value = value.encode( encoding )

    return value

def _getNodeAttribute( node, attr_name, encoding=None ):

    """ Extract a string-valued attribute from node.
    """
    value = _queryNodeAttribute( node, attr_name, _marker, encoding )

    if value is _marker:
        raise ValueError, 'Invaid attribute: %s' % attr_name

    return value

def _queryNodeAttributeBoolean( node, attr_name, default ):

    """ Extract a string-valued attribute from node.

    o Return 'default' if the attribute is not present.
    """
    attr_node = node.attributes.get( attr_name, _marker )

    if attr_node is _marker:
        return default

    value = node.attributes[ attr_name ].nodeValue.lower()

    return value in ( 'true', 'yes', '1' )

def _getNodeAttributeBoolean( node, attr_name ):

    """ Extract a string-valued attribute from node.
    """
    value = node.attributes[ attr_name ].nodeValue.lower()

    return value in ( 'true', 'yes', '1' )

def _coalesceTextNodeChildren( node, encoding=None ):

    """ Concatenate all childe text nodes into a single string.
    """
    from xml.dom import Node
    fragments = []
    node.normalize()
    child = node.firstChild

    while child is not None:

        if child.nodeType == Node.TEXT_NODE:
            fragments.append( child.nodeValue )

        child = child.nextSibling

    joined = ''.join( fragments )

    if encoding is not None:
        joined = joined.encode( encoding )

    return ''.join( [ line.lstrip() for line in joined.splitlines(True) ] )

def _extractDescriptionNode(parent, encoding=None):

    d_nodes = parent.getElementsByTagName('description')
    if d_nodes:
        return _coalesceTextNodeChildren(d_nodes[0], encoding)
    else:
        return ''
