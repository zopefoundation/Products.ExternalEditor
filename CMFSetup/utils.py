""" CMFSetup product utilities

$Id$
"""
import os
from inspect import getdoc

from Globals import package_home

_pkgdir = package_home( globals() )
_wwwdir = os.path.join( _pkgdir, 'www' )
_datadir = os.path.join( _pkgdir, 'data' )
_xmldir = os.path.join( _pkgdir, 'xml' )

def _getDottedName( callable ):

    return '%s.%s' % ( callable.__module__, callable.__name__ )

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
