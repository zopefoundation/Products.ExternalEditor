from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFDefault.RegistrationTool import RegistrationTool


class RegistrationToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_registration \
                import portal_registration as IRegistrationTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IRegistrationTool, RegistrationTool)
        verifyClass(IActionProvider, RegistrationTool)


def test_suite():
    return TestSuite((
        makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
