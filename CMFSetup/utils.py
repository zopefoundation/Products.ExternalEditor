""" CMFSetup product utilities

$Id$
"""
import os
from inspect import getdoc
from types import StringTypes, InstanceType
from xml.sax.handler import ContentHandler

from Globals import package_home

_pkgdir = package_home( globals() )
_wwwdir = os.path.join( _pkgdir, 'www' )
_datadir = os.path.join( _pkgdir, 'data' )
_xmldir = os.path.join( _pkgdir, 'xml' )

def _getDottedName( named ):

    if isinstance( named, StringTypes ):
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

#
#   DOM parsing utilities
#
def _getNodeAttribute( node, attr_name, encoding=None ):

    """ Extract a string-valued attribute from node.
    """
    value = node.attributes[ attr_name ].nodeValue

    if encoding is not None:
        value = value.encode( encoding )

    return value

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

    return joined
