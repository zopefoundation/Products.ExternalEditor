from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFDefault.PropertiesTool import PropertiesTool


class PropertiesToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_properties \
                import portal_properties as IPropertiesTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IPropertiesTool, PropertiesTool)
        verifyClass(IActionProvider, PropertiesTool)


def test_suite():
    return TestSuite((
        makeSuite( PropertiesToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
