##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for SkinsTool module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()


class SkinsContainerTests(TestCase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_skins \
                import SkinsContainer as ISkinsContainer
        from Products.CMFCore.SkinsContainer import SkinsContainer

        verifyClass(ISkinsContainer, SkinsContainer)

    def test_z3interfaces(self):
        try:
            from zope.interface.verify import verifyClass
        except ImportError:
            # BBB: for Zope 2.7
            return
        from Products.CMFCore.interfaces import ISkinsContainer
        from Products.CMFCore.SkinsContainer import SkinsContainer

        verifyClass(ISkinsContainer, SkinsContainer)


class SkinsToolTests(TestCase):

    def _makeOne(self, *args, **kw):
        from Products.CMFCore.SkinsTool import SkinsTool

        return SkinsTool(*args, **kw)

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.interfaces.portal_skins \
                import portal_skins as ISkinsTool
        from Products.CMFCore.interfaces.portal_skins \
                import SkinsContainer as ISkinsContainer
        from Products.CMFCore.SkinsTool import SkinsTool

        verifyClass(IActionProvider, SkinsTool)
        verifyClass(ISkinsContainer, SkinsTool)
        verifyClass(ISkinsTool, SkinsTool)

    def test_z3interfaces(self):
        try:
            from zope.interface.verify import verifyClass
        except ImportError:
            # BBB: for Zope 2.7
            return
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import ISkinsContainer
        from Products.CMFCore.interfaces import ISkinsTool
        from Products.CMFCore.SkinsTool import SkinsTool

        verifyClass(IActionProvider, SkinsTool)
        verifyClass(ISkinsContainer, SkinsTool)
        verifyClass(ISkinsTool, SkinsTool)

    def test_add_invalid_path(self):
        tool = self._makeOne()

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
