import unittest
import Products.PTKTopic.Topic
import Products.PTKTopic.SimpleStringCriterion
import Products.PTKTopic.SimpleIntCriterion

SSC = Products.PTKTopic.SimpleStringCriterion.SimpleStringCriterion
SIC = Products.PTKTopic.SimpleIntCriterion.SimpleIntCriterion
Topic = Products.PTKTopic.Topic.Topic


class TestCase( unittest.TestCase ):
    """
    """
    def setUp( self ):
        pass

    def tearDown( self ):
        pass
    
    def test_Empty( self ):
        topic = Topic()
        assert len( topic.all_meta_types() ) == 3
        query = topic.buildQuery()
        assert len( query ) == 0
    
    def test_Simple( self ):
        topic = Topic()
        topic._setObject( 'foo', SSC( 'foo', 'bar' ) )
        query = topic.buildQuery()
        assert len( query ) == 1
        assert query[ 'foo' ] == 'bar'
        topic._setObject( 'baz', SIC( 'baz', 43 ) )
        query = topic.buildQuery()
        assert len( query ) == 2
        assert query[ 'foo' ] == 'bar'
        assert query[ 'baz' ] == 43
    
    def test_Nested( self ):
        topic = Topic()
        topic._setObject( 'foo', SSC( 'foo', 'bar' ) )
        subtopic = Topic()
        subtopic.id = 'qux'
        subtopic._setObject( 'baz', SSC( 'baz', 'bam' ) )
        topic._setObject( 'qux', subtopic, set_owner=0 )
        subtopic = topic.qux
        query = subtopic.buildQuery()
        assert len( query ) == 2, str( query )
        assert query[ 'foo' ] == 'bar'
        assert query[ 'baz' ] == 'bam'
    
def test_suite():
    return unittest.makeSuite( TestCase )

if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
