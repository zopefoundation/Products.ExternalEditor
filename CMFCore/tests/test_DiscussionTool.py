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

from Products.CMFCore.DiscussionTool import DiscussionTool
from Products.CMFCore.DiscussionTool import OldDiscussable


class DiscussionToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_discussion \
                import oldstyle_portal_discussion as IOldstyleDiscussionTool
        from Products.CMFCore.interfaces.portal_actions \
                import OldstyleActionProvider as IOldstyleActionProvider

        verifyClass(IOldstyleDiscussionTool, DiscussionTool)
        verifyClass(IOldstyleActionProvider, DiscussionTool)


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
