import unittest
import Products.CMFTopic.Topic
import Products.CMFTopic.SimpleStringCriterion
import Products.CMFTopic.SimpleIntCriterion

SSC = Products.CMFTopic.SimpleStringCriterion.SimpleStringCriterion
SIC = Products.CMFTopic.SimpleIntCriterion.SimpleIntCriterion
Topic = Products.CMFTopic.Topic.Topic


class TestTopic(unittest.TestCase):
    """ Test all the general Topic cases  """

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty( self ):
        topic = Topic('top')
        query = topic.buildQuery()
        assert len( query ) == 0
    
    def test_Simple( self ):
        topic = Topic('top')
        topic._setObject('crit__foo', SSC('crit__foo', 'foo'))
        topic.crit__foo.edit('bar')
        query = topic.buildQuery()
        assert len(query) == 1
        assert query['foo'] == 'bar'

        topic._setObject('crit__baz', SIC('crit__baz', 'baz'))
        topic.crit__baz.edit(43)
        query = topic.buildQuery()
        assert len(query) == 2
        assert query['foo'] == 'bar'
        assert query['baz'] == 43
    
    def test_Nested( self ):
        topic = Topic('top')
        topic._setObject('crit__foo', SSC('crit__foo', 'foo'))
        topic.crit__foo.edit('bar')
        subtopic = Topic('qux')
        subtopic._setObject('crit__baz', SSC('crit__baz', 'baz' ))
        subtopic.crit__baz.edit('bam')
        topic._setObject('qux', subtopic, set_owner=0)
        subtopic = topic.qux
        query = subtopic.buildQuery()
        assert len(query) == 2, str(query)
        assert query['foo'] == 'bar'
        assert query['baz'] == 'bam'

        subtopic.acquireCriteria = 0
        query = subtopic.buildQuery()
        assert len(query) == 1
        assert query['baz'] == 'bam'

def test_suite():
    return unittest.makeSuite(TestTopic)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
