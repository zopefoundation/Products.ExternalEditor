from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.UndoTool import UndoTool


class UndoToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_undo \
                import portal_undo as IUndoTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IUndoTool, UndoTool)
        verifyClass(IActionProvider, UndoTool)


def test_suite():
    return TestSuite((
        makeSuite( UndoToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
