import unittest
import Zope

class DummyCachingManager:
    def getHTTPCachingHeaders( self, content, view_name, keywords ):
        return ( ( 'foo', 'Foo' ), ( 'bar', 'Bar' ) )

from Products.CMFCore.tests.base.testcase import RequestTest, SecurityTest

class FSImageTests( RequestTest ):

    def _makeOne( self, id, filename ):

        from Products.CMFCore.FSImage import FSImage
        from Products.CMFCore.tests.test_DirectoryView import skin_path_name
        import os.path

        return FSImage( id, os.path.join( skin_path_name, filename ) )

    def _extractFile( self ):

        from Products.CMFCore.tests.test_DirectoryView import skin_path_name
        import os.path

        path = os.path.join( skin_path_name, 'test_image.gif' )
        f = open( path )
        try:
            data = f.read()
        finally:
            f.close()

        return path, data

    def test_ctor( self ):

        path, ref = self._extractFile()

        image = self._makeOne( 'test_image', 'test_image.gif' )
        image = image.__of__( self.root )

        self.assertEqual( image.get_size(), len( ref ) )
        self.assertEqual( image._data, ref )

    def test_index_html( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        image = self._makeOne( 'test_image', 'test_image.gif' )
        image = image.__of__( self.root )

        data = image.index_html( self.REQUEST, self.RESPONSE )

        self.assertEqual( len( data ), len( ref ) )
        self.assertEqual( data, ref )
        #
        #   ICK!  'HTTPResponse.getHeader' doesn't case-flatten the key!
        #
        self.assertEqual( self.RESPONSE.getHeader( 'Content-Length'.lower() )
                        , len( ref ) )
        self.assertEqual( self.RESPONSE.getHeader( 'Content-Type'.lower() )
                        , 'image/gif' )
        self.assertEqual( self.RESPONSE.getHeader( 'Last-Modified'.lower() )
                        , rfc1123_date( mod_time ) )


    def test_index_html_with_304( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        image = self._makeOne( 'test_image', 'test_image.gif' )
        image = image.__of__( self.root )

        self.REQUEST.environ[ 'IF_MODIFIED_SINCE'
                            ] = '%s;' % rfc1123_date( mod_time+3600 )

        data = image.index_html( self.REQUEST, self.RESPONSE )

        self.assertEqual( data, '' )
        self.assertEqual( self.RESPONSE.getStatus(), 304 )


    def test_index_html_without_304( self ):

        path, ref = self._extractFile()

        import os
        from webdav.common import rfc1123_date

        mod_time = os.stat( path )[ 8 ]

        image = self._makeOne( 'test_image', 'test_image.gif' )
        image = image.__of__( self.root )

        self.REQUEST.environ[ 'IF_MODIFIED_SINCE'
                            ] = '%s;' % rfc1123_date( mod_time-3600 )

        data = image.index_html( self.REQUEST, self.RESPONSE )

        self.failUnless( data, '' )
        self.assertEqual( self.RESPONSE.getStatus(), 200 )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FSImageTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

