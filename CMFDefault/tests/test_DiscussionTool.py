from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFDefault.DiscussionTool import DiscussionTool


class DiscussionToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_discussion \
                import portal_discussion as IDiscussionTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IDiscussionTool, DiscussionTool)
        verifyClass(IActionProvider, DiscussionTool)


def test_suite():
    return TestSuite((
        makeSuite( DiscussionToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
