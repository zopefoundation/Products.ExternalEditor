""" CMFSetup product:  unit test utilities.
"""
import os
import shutil

from Products.CMFCore.tests.base.testcase import SecurityRequestTest


class BaseRegistryTests( SecurityRequestTest ):

    def _makeOne( self, *args, **kw ):

        # Derived classes must implement _getTargetClass
        return self._getTargetClass()( *args, **kw )

    def _compareDOM( self, found_text, expected_text ):

        from xml.dom.minidom import parseString
        found = parseString( found_text )
        expected = parseString( expected_text )
        self.assertEqual( found.toxml(), expected.toxml() )

def _clearTestDirectory( root_path ):

    if os.path.exists( root_path ):
        shutil.rmtree( root_path )
    
def _makeTestFile( filename, root_path, contents ):

    path, filename = os.path.split( filename )

    subdir = os.path.join( root_path, path )

    if not os.path.exists( subdir ):
        os.makedirs( subdir )

    fqpath = os.path.join( subdir, filename )

    file = open( fqpath, 'w' )
    file.write( contents )
    file.close()
    return fqpath

class TestBase( SecurityRequestTest ):

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def setUp( self ):

        SecurityRequestTest.setUp( self )
        self._clearTempDir()

    def tearDown( self ):

        self._clearTempDir()
        SecurityRequestTest.tearDown( self )

    def _clearTempDir( self ):

        _clearTestDirectory( self._PROFILE_PATH )

    def _makeFile( self, filename, contents ):

        return _makeTestFile( filename, self._PROFILE_PATH, contents )

def dummy_handler( context ):

    pass
