import unittest

class TestTopic(unittest.TestCase):
    """
        Test all the general Topic cases
    """

    def test_Empty( self ):

        from Products.CMFTopic.Topic import Topic
        topic = Topic('top')

        query = topic.buildQuery()
        self.assertEqual( len( query ), 0 )
    
    def test_Simple( self ):

        from Products.CMFTopic.Topic import Topic
        topic = Topic('top')
        topic.addCriterion( 'foo', 'String Criterion' )
        topic.getCriterion( 'foo' ).edit( 'bar' )

        query = topic.buildQuery()
        self.assertEqual( len(query), 1 )
        self.assertEqual( query['foo'], 'bar' )

        topic.addCriterion( 'baz', 'Integer Criterion' )
        topic.getCriterion( 'baz' ).edit( 43 )

        query = topic.buildQuery()
        self.assertEqual( len( query ), 2 )
        self.assertEqual( query[ 'foo' ], 'bar' )
        self.assertEqual( query[ 'baz' ], 43 )
    
    def test_Nested( self ):

        from Products.CMFTopic.Topic import Topic
        topic = Topic('top')

        topic.addCriterion( 'foo', 'String Criterion' )
        topic.getCriterion( 'foo' ).edit( 'bar' )

        topic.addSubtopic( 'qux' )
        subtopic = topic.qux

        subtopic.addCriterion( 'baz', 'String Criterion' )
        subtopic.getCriterion( 'baz' ).edit( 'bam' )

        query = subtopic.buildQuery()
        self.assertEqual( len( query ), 2 )
        self.assertEqual( query['foo'], 'bar' )
        self.assertEqual( query['baz'], 'bam' )

        subtopic.acquireCriteria = 0
        query = subtopic.buildQuery()
        self.assertEqual( len( query ), 1 )
        self.assertEqual( query['baz'], 'bam' )

def test_suite():
    return unittest.makeSuite(TestTopic)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
