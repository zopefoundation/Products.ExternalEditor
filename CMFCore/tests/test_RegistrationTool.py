from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass


class RegistrationToolTests(TestCase):

    def _makeOne(self):
        from Products.CMFCore.RegistrationTool import RegistrationTool

        return RegistrationTool()

    def test_generatePassword(self):
        rtool = self._makeOne()
        self.failUnless( len( rtool.generatePassword() ) >= 5 )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_registration \
                import portal_registration as IRegistrationTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.RegistrationTool import RegistrationTool

        verifyClass(IRegistrationTool, RegistrationTool)
        verifyClass(IActionProvider, RegistrationTool)


def test_suite():
    return TestSuite((
        makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
