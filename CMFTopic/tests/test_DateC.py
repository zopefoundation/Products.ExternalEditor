import unittest
import Products.CMFTopic.DateCriteria
from DateTime.DateTime import DateTime

FriendlyDate = Products.CMFTopic.DateCriteria.FriendlyDateCriterion

class TestFriendlyDate(unittest.TestCase):
    lessThanFiveDaysOld = {
        'value': 4,
        'operation': 'min',
        'daterange': 'old',
        }

    lessThanOneMonthAhead = {
        'value': 30,
        'operation': 'max',
        'daterange': 'ahead',
        }

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty(self):
        friendly = FriendlyDate('foo', 'foofield')
        assert friendly.getId() == 'foo'
        assert friendly.field == 'foofield'
        assert friendly.value == None, 'Value should be None'
        assert friendly.operation == 'min', 'Operator should be min'
        assert friendly.daterange == 'old'
        assert len(friendly.getCriteriaItems()) == 0

    def test_ListOfDefaultDates(self):
        friendly = FriendlyDate('foo','foofield')
        d = friendly.defaultDateOptions()
        assert d[1][0] == 2, 'Expected 2, got %s' % d[1][0]

    def test_Basic(self):
        friendly = FriendlyDate('foo', 'foofield')
        friendly.edit(value=None)
        assert friendly.value == None
        assert friendly.daterange == 'old'
        assert friendly.operation == 'min'
        
        apply(friendly.edit, (), self.lessThanFiveDaysOld)
        assert friendly.value == 4
        assert friendly.operation == 'min'
        assert friendly.daterange == 'old'

        # Bogus value on the operation
        self.assertRaises(ValueError, friendly.edit, 4, 'min:max', 'new')

    def test_StringAsValue(self):
        friendly = FriendlyDate('foo', 'foofield')
        friendly.edit('4')
        assert friendly.value == 4

        friendly.edit('-4')
        assert friendly.value == -4

        friendly.edit('')
        assert friendly.value is None

        # Bogus value on the, well, value
        self.assertRaises(ValueError, friendly.edit, 'blah')

    def test_FiveDaysOld(self):
        date = (DateTime() - 4).Date()
        friendly = FriendlyDate('foo', 'foofield')
        apply(friendly.edit, (), self.lessThanFiveDaysOld)

        result = friendly.getCriteriaItems()
        assert friendly.daterange == 'old'
        
        assert len(result) == 2
        assert result[0][0] == 'foofield'
        assert result[0][1].Date() == date, 'Result %s not expected %s' % (
            result[0][1].Date(), date)
        assert result[1][0] == 'foofield_usage'
        assert result[1][1] == 'range:min'

    def test_OneMonthAhead(self):
        date = (DateTime() + 30).Date()
        friendly = FriendlyDate('foo', 'foofield')
        apply(friendly.edit, (), self.lessThanOneMonthAhead)
        result = friendly.getCriteriaItems()
        assert friendly.daterange == 'ahead'

        assert result[0][1].Date() == date, 'Result %s not expected %s' % (
            result[0][1].Date(), date)
        assert result[1][1] == 'range:max'

def test_suite():
    return unittest.makeSuite(TestFriendlyDate)

def main():
    unittest.TextTestRunner().run(test_suite())
    
if __name__ == '__main__':
    main()
