import Zope
from unittest import TestSuite, makeSuite, main

from Products.CMFCore.tests.base.testcase import \
     SecurityTest

from Products.CMFCore.tests.base.utils import \
     has_path

from Products.CMFCore.tests.base.dummy import \
     DummyFTI

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.WorkflowTool import WorkflowTool

from Products.CMFDefault.DiscussionTool import \
     DiscussionTool, DiscussionNotAllowed

from Products.CMFDefault.Document import Document
from Products.CMFDefault.URLTool import URLTool

class DiscussionTests( SecurityTest ):

    def setUp( self ):
        
        SecurityTest.setUp(self)
        
        root = self.root
        root._setObject( 'portal_discussion', DiscussionTool() )
        self.discussion_tool = root.portal_discussion
        root._setObject( 'portal_catalog', CatalogTool() )
        self.catalog_tool = root.portal_catalog
        root._setObject( 'portal_url', URLTool() )
        self.url_tool = root.portal_url
        root._setObject( 'portal_workflow', WorkflowTool() ) 
        self.workflow_tool = root.portal_workflow
        root._setObject( 'portal_types', TypesTool() )
        types_tool = self.types_tool = root.portal_types
        try: root._delObject('test')
        except AttributeError: pass
        root._setObject( 'test', Document( 'test' ) )
            
    def test_policy( self ):

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
        self.types_tool._setObject( 'Document', DummyFTI )
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
        test = self.root.test
        test.allow_discussion = 1
        talkback = self.discussion_tool.getDiscussionFor( test )
        assert talkback._getDiscussable() == test
        assert talkback._getDiscussable( outer=1 ) == test
        assert not talkback.hasReplies( test )
        assert len( talkback.getReplies() ) == 0

        reply_id = talkback.createReply( title='test', text='blah' )
        assert talkback.hasReplies( test )
        assert len( talkback.getReplies() ) == 1
        assert talkback.getReply( reply_id )

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

    def test_itemCataloguing( self ):

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

        test = self.root.test

        test.allow_discussion = 1
        talkback = self.discussion_tool.getDiscussionFor( test )
        talkback.createReply( title='test'
                            , text='blah'
                            )
        self.root._delObject( 'test' )
        assert len( self.catalog_tool ) == 0

    def test_deleteReplies(self):
        test = self.root.test
        test.allow_discussion = 1

        talkback = self.discussion_tool.getDiscussionFor(test)
        id1 = talkback.createReply(title='test1', text='blah')
        reply1 = talkback.getReply(id1)
        talkback1 = self.discussion_tool.getDiscussionFor(reply1)
        id2 = talkback1.createReply(title='test2', text='blah')
        reply2 = talkback1.getReply(id2)
        talkback2 = self.discussion_tool.getDiscussionFor(reply2)
        id3 = talkback2.createReply(title='test3', text='blah')
        reply3 = talkback.getReply(id3)
        talkback3 = self.discussion_tool.getDiscussionFor(reply3)
        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback1.getReplies()), 1)
        self.assertEqual(len(talkback2.getReplies()), 1)
        self.assertEqual(len(talkback3.getReplies()), 0)

        talkback.deleteReply(id2)
        self.assertEqual(len(talkback.getReplies()), 1)
        reply1 = talkback.getReply(id1)
        talkback1 = self.discussion_tool.getDiscussionFor(reply1)
        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback1.getReplies()), 0)

def test_suite():
    return TestSuite((
        makeSuite( DiscussionTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
