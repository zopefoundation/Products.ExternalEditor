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

    def _encode( self, content ):

        if self._encoding is None:
            return content

        return content.encode( self._encoding )

