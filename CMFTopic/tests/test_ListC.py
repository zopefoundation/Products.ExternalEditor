import unittest
import Products.CMFTopic.ListCriterion

LISTC = Products.CMFTopic.ListCriterion.ListCriterion


class TestCase( unittest.TestCase ):
    """
    """
    def setUp( self ):
        pass

    def tearDown( self ):
        pass
    
    def test_Empty( self ):
        listc = LISTC('foo', 'foofield')
        assert listc.id == 'foo'
        assert listc.field == 'foofield'
        assert listc.value == ('',)
        assert len(listc.getCriteriaItems()) == 0
    
    def test_Nonempty( self ):
        listc = LISTC( 'foo', 'foofield' )
        listc.edit('bar\nbaz')
        assert listc.id == 'foo'
        assert listc.field == 'foofield'
        assert listc.value == ( 'bar', 'baz' )
        items =listc.getCriteriaItems()
        assert len( items ) == 1
        assert len( items[0] ) == 2
        assert items[0][0] == 'foofield'
        assert items[0][1] == ( 'bar', 'baz' )
        abc = [ 'a', 'b', 'c' ]
        listc.edit( abc )
        items =listc.getCriteriaItems()
        assert items[0][1] == tuple( abc )

def test_suite():
    return unittest.makeSuite( TestCase )

if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
