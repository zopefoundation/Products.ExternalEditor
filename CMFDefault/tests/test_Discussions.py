import Zope
import unittest, string

from AccessControl import SecurityManager
from Acquisition import aq_base, aq_inner

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.TypesTool import TypesTool, FactoryTypeInformation
from Products.CMFCore.WorkflowTool import WorkflowTool

from Products.CMFDefault.DiscussionTool import DiscussionTool\
                                             , DiscussionNotAllowed

from Products.CMFDefault.Document import Document
from Products.CMFDefault.URLTool import URLTool

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self, accessed, container, name, value, context, roles,
                 *args, **kw ):
        return 1
    
    def checkPermission( self, permission, object, context ) :
        return 1


class DiscussionTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy( self._policy )
        self.connection = Zope.DB.open()
        self.root = self.connection.root()[ 'Application' ]
        self.root._setObject( 'portal_discussion', DiscussionTool() )
        self.discussion_tool = self.root.portal_discussion
        self.root._setObject( 'portal_catalog', CatalogTool() )
        self.catalog_tool = self.root.portal_catalog
        self.root._setObject( 'portal_url', URLTool() )
        self.url_tool = self.root.portal_url
        self.root._setObject( 'portal_workflow', WorkflowTool() ) 
        self.workflow_tool = self.root.portal_workflow
        self.root._setObject( 'portal_types', TypesTool() )
        types_tool = self.types_tool = self.root.portal_types
    
    def tearDown( self ):
        del self.types_tool
        del self.workflow_tool
        del self.url_tool
        del self.discussion_tool
        del self.catalog_tool
        del self.root
        del self._policy
        get_transaction().abort()
        self.connection.close()

    def test_policy( self ):

        self.root._setObject( 'test', Document( 'test' ) )
        test = self.root.test
        self.assertRaises( DiscussionNotAllowed
                         , self.discussion_tool.getDiscussionFor
                         , test
                         )
        assert getattr( test, 'talkback', None ) is None

        test.allow_discussion = 1
        assert self.discussion_tool.getDiscussionFor( test )
        assert test.talkback

        del test.talkback
        del test.allow_discussion
        FTI = FactoryTypeInformation
        self.types_tool._setObject( 'Document'
                                  , FTI( 'Document'
                                       , meta_type=Document.meta_type
                                       , product='CMFDefault'
                                       , factory='addDocument'
                                       )
                                  )
        self.assertRaises( DiscussionNotAllowed
                         , self.discussion_tool.getDiscussionFor
                         , test
                         )
        assert getattr( test, 'talkback', None ) is None

        self.types_tool.Document.allow_discussion = 1
        assert self.discussion_tool.getDiscussionFor( test )
        assert test.talkback

        del test.talkback
        self.types_tool.Document.allow_discussion = 0
        self.assertRaises( DiscussionNotAllowed
                         , self.discussion_tool.getDiscussionFor
                         , test
                         )
        assert getattr( test, 'talkback', None ) is None

        test.allow_discussion = 1
        assert self.discussion_tool.getDiscussionFor( test )
        assert test.talkback
    
    def test_nestedReplies( self ):
        self.root._setObject( 'test', Document( 'test' ) )
        test = self.root.test
        test.allow_discussion = 1
        talkback = self.discussion_tool.getDiscussionFor( test )
        assert talkback._getDiscussable() == test
        assert talkback._getDiscussable( outer=1 ) == test
        assert not talkback.hasReplies( test )
        assert len( talkback.getReplies() ) == 0

        talkback.createReply( title='test'
                            , text='blah'
                            )
        assert talkback.hasReplies( test )
        assert len( talkback.getReplies() ) == 1

        reply1 = talkback.getReplies()[0]
        items = talkback._container.items()
        assert items[0][0] == reply1.getId()
        assert reply1.inReplyTo() == test

        parents = reply1.parentsInThread()
        assert len( parents ) == 1
        assert test in parents

        talkback1 = self.discussion_tool.getDiscussionFor( reply1 )
        assert talkback == talkback1
        assert len( talkback1.getReplies() ) == 0
        assert len( talkback.getReplies() ) == 1

        talkback1.createReply( title='test2'
                             , text='blah2'
                             )
        assert len( talkback._container ) == 2
        assert talkback1.hasReplies( reply1 )
        assert len( talkback1.getReplies() ) == 1
        assert len( talkback.getReplies() ) == 1

        reply2 = talkback1.getReplies()[0]
        assert reply2.inReplyTo() == reply1

        parents = reply2.parentsInThread()
        assert len( parents ) == 2
        assert parents[ 0 ] == test
        assert parents[ 1 ] == reply1

        parents = reply2.parentsInThread( 1 )
        assert len( parents ) == 1
        assert parents[ 0 ] == reply1

    def test_itemCatloguing( self ):

        self.root._setObject( 'test', Document( 'test' ) )
        test = self.root.test
        catalog = self.catalog_tool._catalog
        test.allow_discussion = 1
        assert len( self.catalog_tool ) == 1
        assert has_path( catalog, test.getPhysicalPath() )
        talkback = self.discussion_tool.getDiscussionFor( test )
        assert talkback.getPhysicalPath() == ( '', 'test', 'talkback' ), \
            talkback.getPhysicalPath()
        talkback.createReply( title='test'
                            , text='blah'
                            )
        assert len( self.catalog_tool ) == 2
        for reply in talkback.getReplies():
            assert has_path( catalog, reply.getPhysicalPath() )
            assert has_path( catalog
                           , '/test/talkback/%s' % reply.getId() )

        reply1 = talkback.getReplies()[0]
        talkback1 = self.discussion_tool.getDiscussionFor( reply1 )
        talkback1.createReply( title='test2'
                             , text='blah2'
                             )
        for reply in talkback.getReplies():
            assert has_path( catalog, reply.getPhysicalPath() )
            assert has_path( catalog
                           , '/test/talkback/%s' % reply.getId() )
        for reply in talkback1.getReplies():
            assert has_path( catalog, reply.getPhysicalPath() )
            assert has_path( catalog
                           , '/test/talkback/%s' % reply.getId() )

    def test_deletePropagation( self ):

        self.root._setObject( 'test', Document( 'test' ) )
        test = self.root.test

        test.allow_discussion = 1
        talkback = self.discussion_tool.getDiscussionFor( test )
        talkback.createReply( title='test'
                            , text='blah'
                            )
        self.root._delObject( 'test' )
        assert len( self.catalog_tool ) == 0

def has_path( catalog, path ):
    """
        Verify that catalog has an object at path.
    """
    if type( path ) is type( () ):
        path = string.join( path, '/' )
    rids = map( lambda x: x.data_record_id_, catalog.searchResults() )
    for rid in rids:
        if catalog.getpath( rid ) == path:
            return 1
    return 0

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( DiscussionTests ) )
    return suite

def run():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    run()
