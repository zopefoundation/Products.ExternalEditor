from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFDefault.MembershipTool import MembershipTool


class MembershipToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_membership \
                import portal_membership as IMembershipTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMembershipTool, MembershipTool)
        verifyClass(IActionProvider, MembershipTool)


def test_suite():
    return TestSuite((
        makeSuite( MembershipToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
