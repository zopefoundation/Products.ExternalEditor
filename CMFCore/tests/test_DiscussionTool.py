from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.DiscussionTool import DiscussionTool
from Products.CMFCore.DiscussionTool import OldDiscussable


class DiscussionToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_discussion \
                import oldstyle_portal_discussion as IOldstyleDiscussionTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IOldstyleDiscussionTool, DiscussionTool)
        verifyClass(IActionProvider, DiscussionTool)


class OldDiscussableTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Discussions \
                import OldDiscussable as IOldDiscussable

        verifyClass(IOldDiscussable, OldDiscussable)


def test_suite():
    return TestSuite((
        makeSuite( DiscussionToolTests ),
        makeSuite( OldDiscussableTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
