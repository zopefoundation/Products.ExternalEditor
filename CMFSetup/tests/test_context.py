""" Unit tests for import / export contexts.

$Id$
"""

import unittest
import os
from StringIO import StringIO

from OFS.Folder import Folder

from Products.CMFCore.tests.base.testcase import SecurityRequestTest

from common import FilesystemTestBase
from common import TarballTester
from common import _makeTestFile
from conformance import ConformsToISetupContext
from conformance import ConformsToIImportContext
from conformance import ConformsToIExportContext


class DummySite( Folder ):

    pass

class ImportContextTests( FilesystemTestBase
                        , ConformsToISetupContext
                        , ConformsToIImportContext
                        ):

    _PROFILE_PATH = '/tmp/ICTTexts'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import ImportContext
        return ImportContext

    def test_readDataFile_nonesuch( self ):

        _FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( _FILENAME ), None )

    def test_readDataFile_simple( self ):

        from string import printable
        _FILENAME = 'simple.txt'
        self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( _FILENAME ), printable )

    def test_readDataFile_subdir( self ):

        from string import printable
        _FILENAME = 'subdir/nested.txt'
        self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.readDataFile( _FILENAME ), printable )

    def test_getLastModified_nonesuch( self ):

        _FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( _FILENAME ), None )

    def test_getLastModified_simple( self ):

        from string import printable
        _FILENAME = 'simple.txt'
        fqpath = self._makeFile( _FILENAME, printable )
        timestamp = os.path.getmtime( fqpath )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( _FILENAME ), timestamp )

    def test_getLastModified_nested( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( _FILENAME, printable )
        timestamp = os.path.getmtime( fqpath )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( _FILENAME ), timestamp )

    def test_getLastModified_directory( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( _FILENAME, printable )
        path, file = os.path.split( fqpath )
        timestamp = os.path.getmtime( path )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.getLastModified( _SUBDIR ), timestamp )

    def test_isDirectory_nonesuch( self ):

        _FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( _FILENAME ), None )

    def test_isDirectory_simple( self ):

        from string import printable
        _FILENAME = 'simple.txt'
        fqpath = self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( _FILENAME ), False )

    def test_isDirectory_nested( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( _FILENAME ), False )

    def test_isDirectory_directory( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        fqpath = self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.isDirectory( _SUBDIR ), True )

    def test_listDirectory_nonesuch( self ):

        _FILENAME = 'nonesuch.txt'

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( _FILENAME ), None )

    def test_listDirectory_simple( self ):

        from string import printable
        _FILENAME = 'simple.txt'
        self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( _FILENAME ), None )

    def test_listDirectory_nested( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        self.assertEqual( ctx.listDirectory( _FILENAME ), None )

    def test_listDirectory_single( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( _SUBDIR )
        self.assertEqual( len( names ), 1 )
        self.failUnless( 'nested.txt' in names )

    def test_listDirectory_multiple( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        self._makeFile( _FILENAME, printable )
        self._makeFile( os.path.join( _SUBDIR, 'another.txt' ), 'ABC' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( _SUBDIR )
        self.assertEqual( len( names ), 2 )
        self.failUnless( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )

    def test_listDirectory_skip_implicit( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        self._makeFile( _FILENAME, printable )
        self._makeFile( os.path.join( _SUBDIR, 'another.txt' ), 'ABC' )
        self._makeFile( os.path.join( _SUBDIR, 'CVS/skip.txt' ), 'DEF' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( _SUBDIR )
        self.assertEqual( len( names ), 2 )
        self.failUnless( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )
        self.failIf( 'CVS' in names )

    def test_listDirectory_skip_explicit( self ):

        from string import printable
        _SUBDIR = 'subdir'
        _FILENAME = os.path.join( _SUBDIR, 'nested.txt' )
        self._makeFile( _FILENAME, printable )
        self._makeFile( os.path.join( _SUBDIR, 'another.txt' ), 'ABC' )
        self._makeFile( os.path.join( _SUBDIR, 'CVS/skip.txt' ), 'DEF' )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        names = ctx.listDirectory( _SUBDIR, ( 'nested.txt', ) )
        self.assertEqual( len( names ), 2 )
        self.failIf( 'nested.txt' in names )
        self.failUnless( 'another.txt' in names )
        self.failUnless( 'CVS' in names )


class ExportContextTests( FilesystemTestBase
                        , ConformsToISetupContext
                        , ConformsToIExportContext
                        ):

    _PROFILE_PATH = '/tmp/ECTTexts'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import ExportContext
        return ExportContext

    def test_writeDataFile_simple( self ):

        from string import printable, digits
        _FILENAME = 'simple.txt'
        fqname = self._makeFile( _FILENAME, printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( _FILENAME, digits, 'text/plain' )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_new_subdir( self ):

        from string import printable, digits
        _SUBDIR = 'subdir'
        _FILENAME = 'nested.txt'
        fqname = os.path.join( self._PROFILE_PATH, _SUBDIR, _FILENAME )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( _FILENAME, digits, 'text/plain', _SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_overwrite( self ):

        from string import printable, digits
        _SUBDIR = 'subdir'
        _FILENAME = 'nested.txt'
        fqname = self._makeFile( os.path.join( _SUBDIR, _FILENAME )
                               , printable )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( _FILENAME, digits, 'text/plain', _SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )

    def test_writeDataFile_existing_subdir( self ):

        from string import printable, digits
        _SUBDIR = 'subdir'
        _FILENAME = 'nested.txt'
        self._makeFile( os.path.join( _SUBDIR, 'another.txt' ), printable )
        fqname = os.path.join( self._PROFILE_PATH, _SUBDIR, _FILENAME )

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._makeOne( site, self._PROFILE_PATH )

        ctx.writeDataFile( _FILENAME, digits, 'text/plain', _SUBDIR )

        self.assertEqual( open( fqname, 'rb' ).read(), digits )


class TarballExportContextTests( FilesystemTestBase
                               , TarballTester
                               , ConformsToISetupContext
                               , ConformsToIExportContext
                               ):

    _PROFILE_PATH = '/tmp/TECT_tests'

    def _getTargetClass( self ):

        from Products.CMFSetup.context import TarballExportContext
        return TarballExportContext

    def test_writeDataFile_simple( self ):

        from string import printable

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt' ] )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )

    def test_writeDataFile_multiple( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar.txt', digits, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt', 'bar.txt' ] )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )
        self._verifyTarballEntry( fileish, 'bar.txt', digits )

    def test_writeDataFile_subdir( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        ctx = self._getTargetClass()( site )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar/baz.txt', digits, 'text/plain' ) 

        fileish = StringIO( ctx.getArchive() )

        self._verifyTarballContents( fileish, [ 'foo.txt', 'bar/baz.txt' ] )
        self._verifyTarballEntry( fileish, 'foo.txt', printable )
        self._verifyTarballEntry( fileish, 'bar/baz.txt', digits )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( ImportContextTests ),
        unittest.makeSuite( ExportContextTests ),
        unittest.makeSuite( TarballExportContextTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
