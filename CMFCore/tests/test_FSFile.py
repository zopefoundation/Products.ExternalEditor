import unittest

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from os.path import join as path_join

from Products.CMFCore.tests.base.dummy import DummyCachingManager
from Products.CMFCore.tests.base.testcase import FSDVTest
from Products.CMFCore.tests.base.testcase import RequestTest


class FSFileTests( RequestTest, FSDVTest):

    def setUp(self):
        FSDVTest.setUp(self)
        RequestTest.setUp(self)

    def tearDown(self):
        RequestTest.tearDown(self)
        FSDVTest.tearDown(self)

    def _makeOne( self, id, filename ):

        from Products.CMFCore.FSFile import FSFile

        return FSFile( id, path_join(self.skin_path_name, filename) )

    def _extractFile( self ):

        path = path_join(self.skin_path_name, 'test_file.swf')
        f = open( path, 'rb' )
        try:
            data = f.read()
        finally:
            f.close()

        return path, data

    def test_ctor( self ):

        path, ref = self._extractFile()

        file = self._makeOne( 'test_file', 'test_file.swf' )
        file = file.__of__( self.root )

        self.assertEqual( file.get_size(), len( ref ) )
        self.assertEqual( file._readFile(0), ref )

    def test_str( self ):
        path, ref = self._extractFile()
        file = self._makeOne( 'test_file', 'test_file.swf' )
        file = file.__of__( self.root )
        self.assertEqual( len(str(file)), len( ref ) )

    def test_index_html( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        file = self._makeOne( 'test_file', 'test_file.swf' )
        file = file.__of__( self.root )

        data = file.index_html( self.REQUEST, self.RESPONSE )

        self.assertEqual( len( data ), len( ref ) )
        self.assertEqual( data, ref )
        # ICK!  'HTTPResponse.getHeader' doesn't case-flatten the key!
        # for Zope versions before 2.6.1: Content-Length has to be stringified
        self.assertEqual( str( self.RESPONSE.getHeader(
                                  'Content-Length'.lower() ) )
                        , str(len(ref)) )
        self.assertEqual( self.RESPONSE.getHeader( 'Content-Type'.lower() )
                        , 'application/octet-stream' )
        self.assertEqual( self.RESPONSE.getHeader( 'Last-Modified'.lower() )
                        , rfc1123_date( mod_time ) )

    def test_index_html_with_304( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        file = self._makeOne( 'test_file', 'test_file.swf' )
        file = file.__of__( self.root )

        self.REQUEST.environ[ 'IF_MODIFIED_SINCE'
                            ] = '%s;' % rfc1123_date( mod_time+3600 )

        data = file.index_html( self.REQUEST, self.RESPONSE )

        self.assertEqual( data, '' )
        self.assertEqual( self.RESPONSE.getStatus(), 304 )

    def test_index_html_without_304( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        file = self._makeOne( 'test_file', 'test_file.swf' )
        file = file.__of__( self.root )

        self.REQUEST.environ[ 'IF_MODIFIED_SINCE'
                            ] = '%s;' % rfc1123_date( mod_time-3600 )

        data = file.index_html( self.REQUEST, self.RESPONSE )

        self.failUnless( data, '' )
        self.assertEqual( self.RESPONSE.getStatus(), 200 )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FSFileTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
