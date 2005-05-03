""" Unit tests for 'zuite' module.

$Id$
"""
import unittest
try:
    import Zope2
except ImportError:
    # BBB: for Zope 2.7
    import Zope as Zope2
Zope2.startup()
try:
    import transaction
except ImportError:
    # BBB: for Zope 2.7
    class BBBTransaction:

        def begin(self):
            get_transaction().begin()

        def commit(self, sub=False):
            get_transaction().commit(sub)

        def abort(self, sub=False):
            get_transaction().abort(sub)

    transaction = BBBTransaction()

class DummyResponse:

    def __init__( self ):
        self._headers = {}
        self._body = None

    def setHeader( self, key, value ):
        self._headers[ key ] = value

    def write( self, body ):
        self._body = body

class ZuiteTests( unittest.TestCase ):

    _OLD_NOW = _MARKER = object()

    def setUp( self ):
        from Testing.makerequest import makerequest
        self.connection = Zope2.DB.open()
        self.root =  self.connection.root()[ 'Application' ]
        transaction.begin()
        root = self.root = makerequest( self.root )

    def tearDown( self ):

        if self._OLD_NOW is not self._MARKER:
            self._setNow( self._OLD_NOW )

        transaction.abort()
        self.connection.close()

    def _getTargetClass( self ):

        from Products.Zelenium.zuite import Zuite
        return Zuite

    def _makeOne( self, id='testing', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def _setNow( self, value ):

        from DateTime.DateTime import DateTime
        from Products.Zelenium import zuite

        if isinstance( value, str ):
            value = DateTime( value )

        old, zuite._NOW = zuite._NOW, value
        return old

    def _verifyArchive( self, bits, contents ):
        import StringIO
        import zipfile
        stream = StringIO.StringIO( bits )
        archive = zipfile.ZipFile( stream, 'r' )
        names = archive.namelist()

        self.assertEqual( len( contents ), len( names ), (contents, names) )

        for name in names:
            if name not in contents:
                raise AssertionError, 'Extra name in archive: %s' % name

        for name in contents:
            if name not in names:
                raise AssertionError, 'Missing name in archive: %s' % name

    def _listDefaultArchiveNames( self ):

        from Products.Zelenium.zuite import _SUPPORT_FILES

        expected_names = _SUPPORT_FILES.keys()
        expected_names.append( 'index.html' )
        expected_names.append( 'testSuite.html' )

        return expected_names

    def _makeFile( self, id, title=None, file=None ):

        from OFS.Image import File

        if title is None:
            title = 'File %s' % id

        if file is None:
            file = ''

        return File( id, title, file )

    def test_empty( self ):

        zuite = self._makeOne()
        self.assertEqual( len( zuite.test_case_metatypes ), 2 )
        self.failUnless( 'File' in zuite.test_case_metatypes )
        self.failUnless( 'Page Template' in zuite.test_case_metatypes )
        self.assertEqual( len( zuite.listTestCases() ), 0 )

    def test_getZipFileName( self ):

        _ID = 'gzf'
        _NOW = '2005-05-02'
        self._OLD_NOW = self._setNow( _NOW )

        zuite = self._makeOne( _ID )
        self.assertEqual( zuite.getZipFileName()
                        , '%s-%s.zip' % ( _ID, _NOW ) )

    def test_manage_getZipFile_empty( self ):


        _ID = 'mgzf_empty'
        zuite = self._makeOne( _ID ).__of__( self.root )
        response = DummyResponse()

        zuite.manage_getZipFile( archive_name='empty.zip', RESPONSE=response )

        self.assertEqual( response._headers[ 'Content-type' ]
                        , 'application/zip' )
        self.assertEqual( response._headers[ 'Content-disposition' ]
                        , 'inline;filename=empty.zip' )
        self.assertEqual( response._headers[ 'Content-length' ]
                        , str( len( response._body ) ) )

        self._verifyArchive( response._body, self._listDefaultArchiveNames() )

    def test_manage_getZipFile_default_name( self ):

        _ID = 'mgzf'
        _NOW = '2005-05-02'
        _FILENAME = 'test_one'

        self._OLD_NOW = self._setNow( _NOW )

        zuite = self._makeOne( _ID ).__of__( self.root )
        zuite._setObject( _FILENAME, self._makeFile( _FILENAME ) )
        response = DummyResponse()

        zuite.manage_getZipFile( RESPONSE=response )

        self.assertEqual( response._headers[ 'Content-type' ]
                        , 'application/zip' )
        self.assertEqual( response._headers[ 'Content-disposition' ]
                        , 'inline;filename=%s-%s.zip' % ( _ID, _NOW ) )
        self.assertEqual( response._headers[ 'Content-length' ]
                        , str( len( response._body ) ) )

        expected = self._listDefaultArchiveNames()
        expected.append( 'test_one.html' )
        self._verifyArchive( response._body, expected )
        
# TODO: def test_listTestCases_simple( self ):
# TODO: def test_listTestCases_recursive( self ):
# TODO: def test_manage_createSnapshot_empty( self ):
# TODO: def test_manage_createSnapshot_default_name( self ):

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( ZuiteTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
