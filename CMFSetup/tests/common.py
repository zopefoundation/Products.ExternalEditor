""" CMFSetup product:  unit test utilities.
"""
import os
import shutil
from tarfile import TarFile

from Products.CMFCore.tests.base.testcase import SecurityRequestTest


class DOMComparator:

    def _compareDOM( self, found_text, expected_text ):

        from xml.dom.minidom import parseString
        found = parseString( found_text )
        expected = parseString( expected_text )
        fxml = found.toxml()
        exml = expected.toxml()

        if fxml != exml:
            print 'Found:'
            print fxml
            print
            print 'Expected:'
            print exml
            print

        self.assertEqual( found.toxml(), expected.toxml() )

class BaseRegistryTests( SecurityRequestTest, DOMComparator ):

    def _makeOne( self, *args, **kw ):

        # Derived classes must implement _getTargetClass
        return self._getTargetClass()( *args, **kw )

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

class FilesystemTestBase( SecurityRequestTest ):

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


class TarballTester( DOMComparator ):

    def _verifyTarballContents( self, fileish, toc_list ):

        fileish.seek( 0L )
        tarfile = TarFile.open( 'foo.tar.gz', fileobj=fileish, mode='r:gz' )
        items = tarfile.getnames()
        items.sort()
        toc_list.sort()

        self.assertEqual( len( items ), len( toc_list ) )
        for i in range( len( items ) ):
            self.assertEqual( items[ i ], toc_list[ i ] )

    def _verifyTarballEntry( self, fileish, entry_name, data ):

        fileish.seek( 0L )
        tarfile = TarFile.open( 'foo.tar.gz', fileobj=fileish, mode='r:gz' )
        extract = tarfile.extractfile( entry_name )
        found = extract.read()
        self.assertEqual( found, data )

    def _verifyTarballEntryXML( self, fileish, entry_name, data ):

        fileish.seek( 0L )
        tarfile = TarFile.open( 'foo.tar.gz', fileobj=fileish, mode='r:gz' )
        extract = tarfile.extractfile( entry_name )
        found = extract.read()
        self._compareDOM( found, data )


class DummyExportContext:

    def __init__( self, site ):
        self._site = site
        self._wrote = []

    def getSite( self ):
        return self._site

    def writeDataFile( self, filename, text, content_type ):
        self._wrote.append( ( filename, text, content_type ) )

class DummyImportContext:

    def __init__( self, site, purge=True ):
        self._site = site
        self._purge = purge
        self._files = {}

    def getSite( self ):
        return self._site

    def getEncoding( self ):
        return None

    def readDataFile( self, filename, subdir=None ):

        if subdir is not None:
            filename = '/'.join( subdir, filename )

        return self._files.get( filename )

    def shouldPurge( self ):

        return self._purge

def dummy_handler( context ):

    pass
