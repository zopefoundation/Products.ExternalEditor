import Zope
import unittest
import re, new
import Globals
from Globals import Persistent 
from Acquisition import Implicit
from AccessControl import SecurityManager
from Products.CMFDefault.Document import Document
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFDefault.Discussions import DiscussionResponse
from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CMFDefault.URLTool import URLTool
from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.CMFDefault.DiscussionItem import *

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate(self, accessed, container, name, value, context, roles,
                 *args, **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        return 1


class DiscussionItem(Document, DiscussionResponse):
    """
    """
    meta_type = 'DItem'
    after_add_called = before_delete_called = 0

    def __init__( self, id, catalog=0 ):
        self.id = id
        self.reset()
        self.catalog = catalog

    def manage_afterAdd( self, item, container ):
        self.after_add_called = 1
        if self.catalog:
            Document.manage_afterAdd( self, item, container )

    def manage_beforeDelete( self, item, container ):
        self.before_delete_called = 1
        if self.catalog:
            DiscussionItem.DiscussionItemContainer.manage_beforeDelete( self, item, container )
    
    def reset( self ):
        self.after_add_called = self.before_delete_called = 0


class DiscussionTests(unittest.TestCase):

    def setUp(self):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        self.root = Zope.app()
    
    def tearDown(self):
        get_transaction().abort()

    def test_deletePropagation(self):
       # import pdb; pdb.set_trace()
        portal_catalog = CatalogTool()
        self.root._setObject('portal_catalog', portal_catalog)
        catalog = self.root.portal_catalog
        portal_discussion = DiscussionTool()
        self.root._setObject('portal_discussion', portal_discussion)
        portal_url = URLTool()
        self.root._setObject('portal_url', portal_url)
        portal_workflow = WorkflowTool()
        self.root._setObject('portal_workflow', portal_workflow) 
        test = Document('test')
        self.root._setObject('test', test)
        test = self.root.test
        test.allow_discussion = 1
        assert len(catalog) == 1
        portal_discussion.createDiscussionFor(test)
        talkback = test.talkback
        talkback.createReply(title='test'
                             , text='blah'
                             )
        foo = talkback.getReplies()[0]
        assert len(catalog) == 2
        self.root._delObject('test')
        assert len(catalog) == 0


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( DiscussionTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
