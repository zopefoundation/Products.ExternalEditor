import unittest
import Products.CMFTopic.SimpleIntCriterion

SIC = Products.CMFTopic.SimpleIntCriterion.SimpleIntCriterion


class TestSimpleInt(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty(self):
        sic = SIC('foo', 'foofield' )
        assert sic.getId() == 'foo'
        assert sic.field == 'foofield'
        assert sic.value == None
        assert len(sic.getCriteriaItems()) == 0
    
    def test_Nonempty(self):
        sic = SIC('foo', 'foofield')
        sic.edit('0')
        assert sic.getId() == 'foo'
        assert sic.field == 'foofield'
        assert sic.value == 0
        items =sic.getCriteriaItems()
        assert len(items) == 1
        assert len(items[0]) == 2
        assert items[0][0] == 'foofield'
        assert items[0][1] == 0

        sic = SIC('foo', 'foofield')
        sic.edit(32)
        assert sic.value == 32
        items =sic.getCriteriaItems()
        assert len(items) == 1
        assert len(items[0]) == 2
        assert items[0][1] == 32

    def test_Range(self):
        sic = SIC('foo', 'foofield')
        sic.edit(32, SIC.MINIMUM)
        items = sic.getCriteriaItems()
        assert len(items) == 2
        assert len(items[0]) == len(items[1]) == 2
        assert items[0][1] == 32
        assert items[1][0] == 'foofield_usage'
        assert items[1][1] == 'range:min'

        sic.direction = SIC.MAXIMUM
        items = sic.getCriteriaItems()
        assert items[1][0] == 'foofield_usage'
        assert items[1][1] == 'range:max'

        sic.direction = SIC.MINMAX
        items = sic.getCriteriaItems()
        assert items[1][0] == 'foofield_usage'
        assert items[1][1] == 'range:min:max'

def test_suite():
    return unittest.makeSuite(TestSimpleInt)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
