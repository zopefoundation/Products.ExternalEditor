import unittest
import Products.CMFTopic.Topic
import Products.CMFTopic.SimpleStringCriterion
import Products.CMFTopic.SimpleIntCriterion

SSC = Products.CMFTopic.SimpleStringCriterion.SimpleStringCriterion
SIC = Products.CMFTopic.SimpleIntCriterion.SimpleIntCriterion
Topic = Products.CMFTopic.Topic.Topic


class TestCase( unittest.TestCase ):
    """ Test all the general Topic cases  """
    def test_Empty( self ):
        topic = Topic('top')
        assert len(topic._criteriaTypes) == 3
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

    def test_EditCriterion(self):
        topic = Topic('top')
        topic._setObject('crit__foo', SSC('crit__foo', 'foo'))
        topic._setObject('crit__bar', SIC('crit__bar', 'bar'))

        class CritRecord:
            pass
        foorec = CritRecord()
        barrec = CritRecord()

        foorec.id = 'crit__foo'
        foorec.value = 'goodfoo'

        barrec.id = 'crit__bar'
        barrec.value = '12'

        query = topic.buildQuery()
        assert len(query) == 0
        topic.editCriteria([foorec, barrec])
        query = topic.buildQuery()
        assert len(query) == 2
        assert query['foo'] == 'goodfoo'
        assert query['bar'] == 12

        barrec.direction = SIC.MINIMUM
        topic.editCriteria([barrec])
        query = topic.buildQuery()
        assert len(query) == 3
        assert query['bar_usage'] == 'range:min'
        assert query['foo'] == 'goodfoo'
        
    
def test_suite():
    return unittest.makeSuite(TestCase)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
