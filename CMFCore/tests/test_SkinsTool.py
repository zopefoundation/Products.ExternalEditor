from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.SkinsTool import SkinsTool


class SkinsToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_skins \
                import portal_skins as ISkinsTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(ISkinsTool, SkinsTool)
        verifyClass(IActionProvider, SkinsTool)


def test_suite():
    return TestSuite((
        makeSuite( SkinsToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
