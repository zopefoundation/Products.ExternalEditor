import unittest
import Products.PTKTopic.ListCriterion

LISTC = Products.PTKTopic.ListCriterion.ListCriterion


class TestCase( unittest.TestCase ):
    """
    """
    def setUp( self ):
        pass

    def tearDown( self ):
        pass
    
    def test_Empty( self ):
        listc = LISTC( 'foo' )
        assert listc.id == 'foo'
        assert listc.value == None
        assert len( listc.getCriteriaItems() ) == 0
    
    def test_Nonempty( self ):
        listc = LISTC( 'foo', 'bar\nbaz' )
        assert listc.id == 'foo'
        assert listc.value == ( 'bar', 'baz' )
        items =listc.getCriteriaItems()
        assert len( items ) == 1
        assert len( items[0] ) == 2
        assert items[0][0] == 'foo'
        assert items[0][1] == ( 'bar', 'baz' )
        abc = [ 'a', 'b', 'c' ]
        listc.edit( abc )
        items =listc.getCriteriaItems()
        assert items[0][1] == tuple( abc )

def test_suite():
    return unittest.makeSuite( TestCase )

if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
