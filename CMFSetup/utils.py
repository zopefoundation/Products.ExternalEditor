""" CMFSetup product utilities

$Id$
"""
import os

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

