import unittest
import Products.CMFTopic.ListCriterion

LISTC = Products.CMFTopic.ListCriterion.ListCriterion


class TestListCriterion(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()
    
    def test_Empty( self ):
        listc = LISTC('foo', 'foofield')
        assert listc.getId() == 'foo'
        assert listc.field == 'foofield'
        assert listc.value == ('',)
        assert len(listc.getCriteriaItems()) == 0
    
    def test_Nonempty( self ):
        listc = LISTC( 'foo', 'foofield' )
        listc.edit('bar\nbaz')
        assert listc.getId() == 'foo'
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
    return unittest.makeSuite(TestListCriterion)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
