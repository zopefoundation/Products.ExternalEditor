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

from Products.CMFCore.SkinsContainer import SkinsContainer
from Products.CMFCore.SkinsTool import SkinsTool


class SkinsContainerTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_skins \
                import SkinsContainer as ISkinsContainer

        verifyClass(ISkinsContainer, SkinsContainer)


class SkinsToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_skins \
                import portal_skins as ISkinsTool
        from Products.CMFCore.interfaces.portal_skins \
                import SkinsContainer as ISkinsContainer
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(ISkinsTool, SkinsTool)
        verifyClass(ISkinsContainer, SkinsTool)
        verifyClass(IActionProvider, SkinsTool)


def test_suite():
    return TestSuite((
        makeSuite(SkinsContainerTests),
        makeSuite(SkinsToolTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
