import unittest
import Products.CMFTopic.SimpleStringCriterion

SSC = Products.CMFTopic.SimpleStringCriterion.SimpleStringCriterion


class TestSimpleString(unittest.TestCase):
    
    def test_Empty( self ):
        ssc = SSC('foo', 'foofield')
        assert ssc.getId() == 'foo'
        assert ssc.field == 'foofield'
        assert ssc.value == ''
        assert len( ssc.getCriteriaItems() ) == 0
    
    def test_Nonempty( self ):
        ssc = SSC('foo', 'foofield')
        ssc.edit('bar')
        assert ssc.getId() == 'foo'
        assert ssc.field == 'foofield'
        assert ssc.value == 'bar'

        items =ssc.getCriteriaItems()
        assert len(items) == 1
        assert len(items[0]) == 2
        assert items[0][0] == 'foofield'
        assert items[0][1] == 'bar'

def test_suite():
    return unittest.makeSuite(TestSimpleString)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
