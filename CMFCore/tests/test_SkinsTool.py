from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

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

    def test_add_invalid_path(self):
        tool = SkinsTool()

        # We start out with no wkin selections
        self.assertEquals(len(tool.getSkinSelections()), 0)
        
        # Add a skin selection with an invalid path element
        paths = 'foo, bar, .svn'
        tool.addSkinSelection('fooskin', paths)

        # Make sure the skin selection exists
        paths = tool.getSkinPath('fooskin')
        self.failIf(paths is None)
        
        # Test for the contents
        self.failIf(paths.find('foo') == -1)
        self.failIf(paths.find('bar') == -1)
        self.failUnless(paths.find('.svn') == -1)


def test_suite():
    return TestSuite((
        makeSuite(SkinsContainerTests),
        makeSuite(SkinsToolTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
