import unittest
from Products.CMFDefault.utils import parseHeadersBody
from string import split

class DefaultUtilsTests(unittest.TestCase):
    COMMON_HEADERS = '''Author: Tres Seaver
Title: Test Products.PTKDemo.utils.parseHeadersBody'''

    MULTILINE_DESCRIPTION = '''Description: this description spans
        multiple lines.'''

    TEST_BODY = '''Body goes here, and can span multiple
lines.  It can even include "headerish" lines, like:

Header: value
'''

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()
    
    def test_NoBody( self ):
        headers, body = parseHeadersBody( '%s\n\n' % self.COMMON_HEADERS )
        assert( len( headers ) == 2, '%d!' % len( headers ) )
        assert( 'Author' in headers.keys() )
        assert( headers[ 'Author' ] == 'Tres Seaver' )
        assert( 'Title' in headers.keys() )
        assert( len( body ) == 0, '%d!' % len( body ) )

    def test_Continuation( self ):
        headers, body = parseHeadersBody( '%s\n%s\n\n'
                                        % ( self.COMMON_HEADERS
                                          , self.MULTILINE_DESCRIPTION
                                          )
                                        )
        assert( len( headers ) == 3, '%d!' % len( headers )  )
        assert( 'Description' in headers.keys() )
        desc_len = len( split( headers[ 'Description' ], '\n' ) )
        assert( desc_len == 2, '%d!' % desc_len )
        assert( len( body ) == 0, '%d!' % len( body ) )
    
    def test_Body( self ):
        headers, body = parseHeadersBody( '%s\n\n%s'
                                        % ( self.COMMON_HEADERS
                                          , self.TEST_BODY
                                          )
                                        )
        assert( len( headers ) == 2, '%d!' % len( headers ) )
        assert( body == self.TEST_BODY )
    
    def test_Preload( self ):
        preloaded = { 'Author' : 'xxx', 'text_format' : 'structured_text' }
        headers, body = parseHeadersBody( '%s\n%s\n\n%s'
                                        % ( self.COMMON_HEADERS
                                          , self.MULTILINE_DESCRIPTION
                                          , self.TEST_BODY
                                          )
                                        , preloaded
                                        )
        assert( len( headers ) == 3, '%d!' % len( headers ) )
        assert( preloaded[ 'Author' ] != headers[ 'Author' ] )
        assert( preloaded[ 'text_format' ] == headers[ 'text_format' ] )

def test_suite():
    return unittest.makeSuite(DefaultUtilsTests)

if __name__ == '__main__':
    result = unittest.TextTestRunner().run(test_suite())

