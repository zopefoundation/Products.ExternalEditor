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

class DummyTool( Folder ):

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


class SnapshotExportContextTests( SecurityRequestTest
                                , ConformsToISetupContext
                                , ConformsToIExportContext
                                ):

    def _getTargetClass( self ):

        from Products.CMFSetup.context import SnapshotExportContext
        return SnapshotExportContext

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def test_writeDataFile_simple_image( self ):

        from OFS.Image import Image
        _FILENAME = 'simple.txt'
        _CONTENT_TYPE = 'image/png'
        png_filename = os.path.join( os.path.split( __file__ )[0]
                                   , 'simple.png' )
        png_file = open( png_filename, 'rb' )
        png_data = png_file.read()
        png_file.close()

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, png_data, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( _FILENAME in snapshot.objectIds() )

        fileobj = snapshot._getOb( _FILENAME )

        self.assertEqual( fileobj.getId(), _FILENAME )
        self.assertEqual( fileobj.meta_type, Image.meta_type )
        self.assertEqual( fileobj.getContentType(), _CONTENT_TYPE )
        self.assertEqual( fileobj.data, png_data )

    def test_writeDataFile_simple_plain_text( self ):

        from string import digits
        from OFS.Image import File
        _FILENAME = 'simple.txt'
        _CONTENT_TYPE = 'text/plain'

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, digits, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( _FILENAME in snapshot.objectIds() )

        fileobj = snapshot._getOb( _FILENAME )

        self.assertEqual( fileobj.getId(), _FILENAME )
        self.assertEqual( fileobj.meta_type, File.meta_type )
        self.assertEqual( fileobj.getContentType(), _CONTENT_TYPE )
        self.assertEqual( str( fileobj ), digits )

    def test_writeDataFile_simple_xml( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        _FILENAME = 'simple.xml'
        _CONTENT_TYPE = 'text/xml'
        _XML = """<?xml version="1.0"?><simple />"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, _XML, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( _FILENAME in snapshot.objectIds() )

        template = snapshot._getOb( _FILENAME )

        self.assertEqual( template.getId(), _FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _XML )
        self.failIf( template.html() )

    def test_writeDataFile_unicode_xml( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        _FILENAME = 'simple.xml'
        _CONTENT_TYPE = 'text/xml'
        _XML = u"""<?xml version="1.0"?><simple />"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, _XML, _CONTENT_TYPE )

        snapshot = tool.snapshots._getOb( 'simple' )

        self.assertEqual( len( snapshot.objectIds() ), 1 )
        self.failUnless( _FILENAME in snapshot.objectIds() )

        template = snapshot._getOb( _FILENAME )

        self.assertEqual( template.getId(), _FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _XML )
        self.failIf( template.html() )

    def test_writeDataFile_subdir_dtml( self ):

        from OFS.DTMLDocument import DTMLDocument
        _FILENAME = 'simple.dtml'
        _CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, _HTML, _CONTENT_TYPE, 'sub1' )

        snapshot = tool.snapshots._getOb( 'simple' )
        sub1 = snapshot._getOb( 'sub1' )

        self.assertEqual( len( sub1.objectIds() ), 1 )
        self.failUnless( _FILENAME in sub1.objectIds() )

        template = sub1._getOb( _FILENAME )

        self.assertEqual( template.getId(), _FILENAME )
        self.assertEqual( template.meta_type, DTMLDocument.meta_type )
        self.assertEqual( template.read(), _HTML )

    def test_writeDataFile_nested_subdirs_html( self ):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        _FILENAME = 'simple.html'
        _CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'simple' )

        ctx.writeDataFile( _FILENAME, _HTML, _CONTENT_TYPE, 'sub1/sub2' )

        snapshot = tool.snapshots._getOb( 'simple' )
        sub1 = snapshot._getOb( 'sub1' )
        sub2 = sub1._getOb( 'sub2' )

        self.assertEqual( len( sub2.objectIds() ), 1 )
        self.failUnless( _FILENAME in sub2.objectIds() )

        template = sub2._getOb( _FILENAME )

        self.assertEqual( template.getId(), _FILENAME )
        self.assertEqual( template.meta_type, ZopePageTemplate.meta_type )
        self.assertEqual( template.read(), _HTML )
        self.failUnless( template.html() )

    def test_writeDataFile_multiple( self ):

        from string import printable
        from string import digits

        site = DummySite( 'site' ).__of__( self.root )
        site.portal_setup = DummyTool( 'portal_setup' )
        tool = site.portal_setup
        ctx = self._makeOne( tool, 'multiple' )

        ctx.writeDataFile( 'foo.txt', printable, 'text/plain' ) 
        ctx.writeDataFile( 'bar.txt', digits, 'text/plain' ) 

        snapshot = tool.snapshots._getOb( 'multiple' )

        self.assertEqual( len( snapshot.objectIds() ), 2 )

        for id in [ 'foo.txt', 'bar.txt' ]:
            self.failUnless( id in snapshot.objectIds() )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( ImportContextTests ),
        unittest.makeSuite( ExportContextTests ),
        unittest.makeSuite( TarballExportContextTests ),
        unittest.makeSuite( SnapshotExportContextTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
