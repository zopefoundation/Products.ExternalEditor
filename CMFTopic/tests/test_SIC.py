import unittest
import Products.PTKTopic.SimpleIntCriterion

SIC = Products.PTKTopic.SimpleIntCriterion.SimpleIntCriterion


class TestCase( unittest.TestCase ):
    """
    """
    def setUp( self ):
        pass

    def tearDown( self ):
        pass
    
    def test_Empty( self ):
        sic = SIC( 'foo' )
        assert sic.id == 'foo'
        assert sic.value == None
        assert len( sic.getCriteriaItems() ) == 0
    
    def test_Nonempty( self ):
        sic = SIC( 'foo', '0' )
        assert sic.id == 'foo'
        assert sic.value == 0
        items =sic.getCriteriaItems()
        assert len( items ) == 1
        assert len( items[0] ) == 2
        assert items[0][0] == 'foo'
        assert items[0][1] == 0

        sic = SIC( 'foo', 32 )
        assert sic.value == 32
        items =sic.getCriteriaItems()
        assert len( items ) == 1
        assert len( items[0] ) == 2
        assert items[0][1] == 32

    def test_Range( self ):
        sic = SIC( 'foo', 32 )
        sic.direction = SIC.MINIMUM
        items = sic.getCriteriaItems()
        assert len( items ) == 2
        assert len( items[0] ) == len( items[1] ) == 2
        assert items[0][1] == 32
        assert items[1][0] == 'foo_usage'
        assert items[1][1] == 'range:min'
        sic.direction = SIC.MAXIMUM
        items = sic.getCriteriaItems()
        assert items[1][0] == 'foo_usage'
        assert items[1][1] == 'range:max'
        sic.direction = SIC.MINMAX
        items = sic.getCriteriaItems()
        assert items[1][0] == 'foo_usage'
        assert items[1][1] == 'range:min:max'

def test_suite():
    return unittest.makeSuite( TestCase )

if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
