#
# Tests for http://zope.org/Collectors/CMF/318
#

from unittest import TestSuite, makeSuite, main

import Testing
import Zope
Zope.startup()

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Products.CMFCore.tests.base.testcase import RequestTest


class DiscussionReplyTest(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        try:
            factory = self.root.manage_addProduct['CMFSetup'].addConfiguredSite
            factory('cmf', 'default', snapshot=False)
            self.portal = self.root.cmf
            # Become a Manager
            self.uf = self.portal.acl_users
            self.uf.userFolderAddUser('manager', '', ['Manager'], [])
            self.login('manager')
            # Make a document
            self.discussion = self.portal.portal_discussion
            self.portal.invokeFactory('Document', id='doc')
            self.discussion.overrideDiscussionFor(self.portal.doc, 1)
            # Publish it
            self.workflow = self.portal.portal_workflow
            self.workflow.doActionFor(self.portal.doc, 'publish')
        except:
            self.tearDown()
            raise

    def tearDown(self):
        noSecurityManager()
        RequestTest.tearDown(self)

    def login(self, name):
        user = self.uf.getUserById(name)
        user = user.__of__(self.uf)
        newSecurityManager(None, user)

    def testDiscussionReply(self):
        self.discussion.getDiscussionFor(self.portal.doc)
        self.portal.doc.talkback.discussion_reply('Title', 'Text')
        reply = self.portal.doc.talkback.objectValues()[0]
        self.assertEqual(reply.Title(), 'Title')
        self.assertEqual(reply.EditableBody(), 'Text')


class DiscussionReplyTestMember(DiscussionReplyTest):

    # Run the test again as another Member, i.e. reply to someone
    # else's document.

    def setUp(self):
        DiscussionReplyTest.setUp(self)
        try:
            self.uf.userFolderAddUser('member', '', ['Member'], [])
            self.login('member')
        except:
            self.tearDown()
            raise


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(DiscussionReplyTest))
    suite.addTest(makeSuite(DiscussionReplyTestMember))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
