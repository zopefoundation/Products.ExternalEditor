from unittest import TestCase, TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFDefault.DiscussionItem import DiscussionItem
from Products.CMFDefault.DiscussionItem import DiscussionItemContainer
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed
from Products.CMFDefault.DiscussionTool import DiscussionTool


class DiscussionItemTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish
        from Products.CMFCore.interfaces.Discussions \
                import DiscussionResponse as IDiscussionResponse
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore

        verifyClass(IDynamicType, DiscussionItem)
        verifyClass(IContentish, DiscussionItem)
        verifyClass(IDublinCore, DiscussionItem)
        verifyClass(ICatalogableDublinCore, DiscussionItem)
        verifyClass(IMutableDublinCore, DiscussionItem)
        verifyClass(IDiscussionResponse, DiscussionItem)


class DiscussionItemContainerTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Discussions \
                import Discussable as IDiscussable

        verifyClass(IDiscussable, DiscussionItemContainer)


class DiscussionTests( SecurityTest ):

    def setUp( self ):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.site._setObject( 'portal_discussion', DiscussionTool() )
        self.site._setObject( 'portal_membership', DummyTool() )
        self.site._setObject( 'portal_types', TypesTool() )

    def _makeDummyContent(self, id, *args, **kw):
        return self.site._setObject( id, DummyContent(id, *args, **kw) )

    def test_policy( self ):
        dtool = self.site.portal_discussion
        ttool = self.site.portal_types
        test = self._makeDummyContent('test')
        self.assertRaises(DiscussionNotAllowed, dtool.getDiscussionFor, test)
        assert getattr( test, 'talkback', None ) is None

        test.allow_discussion = 1
        assert dtool.getDiscussionFor(test)
        assert test.talkback

        del test.talkback
        del test.allow_discussion
        fti = FTIDATA_DUMMY[0].copy()
        ttool._setObject( 'Dummy Content', FTI(**fti) )
        self.assertRaises(DiscussionNotAllowed, dtool.getDiscussionFor, test)
        assert getattr( test, 'talkback', None ) is None

        ti = getattr(ttool, 'Dummy Content')
        ti.allow_discussion = 1
        assert dtool.getDiscussionFor(test)
        assert test.talkback

        del test.talkback
        ti.allow_discussion = 0
        self.assertRaises(DiscussionNotAllowed, dtool.getDiscussionFor, test)
        assert getattr( test, 'talkback', None ) is None

        test.allow_discussion = 1
        assert dtool.getDiscussionFor(test)
        assert test.talkback

    def test_nestedReplies( self ):
        dtool = self.site.portal_discussion
        test = self._makeDummyContent('test')
        test.allow_discussion = 1
        talkback = dtool.getDiscussionFor(test)
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
        self.assertEqual( reply1.getId(), items[0][0] )
        self.assertEqual( reply1.inReplyTo(), test )
        self.assertEqual( reply1.listCreators(), ('dummy',) )

        parents = reply1.parentsInThread()
        assert len( parents ) == 1
        assert test in parents

        talkback1 = dtool.getDiscussionFor(reply1)
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
        ctool = self.site._setObject( 'portal_catalog', CatalogTool() )
        dtool = self.site.portal_discussion
        catalog = ctool._catalog
        test = self._makeDummyContent('test', catalog=1)
        test.allow_discussion = 1

        self.assertEqual( len(ctool), 1 )
        self.failUnless( has_path( catalog, test.getPhysicalPath() ) )
        talkback = dtool.getDiscussionFor(test)
        self.assertEqual( talkback.getPhysicalPath(),
                          ('', 'bar', 'site', 'test', 'talkback') )
        talkback.createReply( title='test'
                            , text='blah'
                            )
        self.assertEqual( len(ctool), 2 )
        for reply in talkback.getReplies():
            self.failUnless( has_path( catalog, reply.getPhysicalPath() ) )
            self.failUnless( has_path( catalog,
                              '/bar/site/test/talkback/%s' % reply.getId() ) )

        reply1 = talkback.getReplies()[0]
        talkback1 = dtool.getDiscussionFor(reply1)
        talkback1.createReply( title='test2'
                             , text='blah2'
                             )
        for reply in talkback.getReplies():
            self.failUnless( has_path( catalog, reply.getPhysicalPath() ) )
            self.failUnless( has_path( catalog,
                              '/bar/site/test/talkback/%s' % reply.getId() ) )
        for reply in talkback1.getReplies():
            self.failUnless( has_path( catalog, reply.getPhysicalPath() ) )
            self.failUnless( has_path( catalog,
                              '/bar/site/test/talkback/%s' % reply.getId() ) )

    def test_deletePropagation( self ):
        ctool = self.site._setObject( 'portal_catalog', CatalogTool() )
        dtool = self.site.portal_discussion
        test = self._makeDummyContent('test', catalog=1)
        test.allow_discussion = 1

        talkback = dtool.getDiscussionFor(test)
        talkback.createReply( title='test'
                            , text='blah'
                            )
        self.assertEqual( len(ctool), 2 )
        self.site._delObject('test')
        self.assertEqual( len(ctool), 0 )

    def test_deleteReplies(self):
        dtool = self.site.portal_discussion
        test = self._makeDummyContent('test')
        test.allow_discussion = 1

        talkback = dtool.getDiscussionFor(test)
        id1 = talkback.createReply(title='test1', text='blah')
        reply1 = talkback.getReply(id1)
        talkback1 = dtool.getDiscussionFor(reply1)
        id2 = talkback1.createReply(title='test2', text='blah')
        reply2 = talkback1.getReply(id2)
        talkback2 = dtool.getDiscussionFor(reply2)
        id3 = talkback2.createReply(title='test3', text='blah')
        reply3 = talkback.getReply(id3)
        talkback3 = dtool.getDiscussionFor(reply3)
        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback1.getReplies()), 1)
        self.assertEqual(len(talkback2.getReplies()), 1)
        self.assertEqual(len(talkback3.getReplies()), 0)

        talkback.deleteReply(id2)
        self.assertEqual(len(talkback.getReplies()), 1)
        reply1 = talkback.getReply(id1)
        talkback1 = dtool.getDiscussionFor(reply1)
        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback1.getReplies()), 0)


def test_suite():
    return TestSuite((
        makeSuite( DiscussionItemTests ),
        makeSuite( DiscussionItemContainerTests ),
        makeSuite( DiscussionTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
