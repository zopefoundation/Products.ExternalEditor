from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.tests.base.dummy import DummyFolder

from Products.CMFDefault.MembershipTool import MembershipTool


class MembershipToolTests(TestCase):

    def setUp(self):
        self.site = DummyFolder()

    def _makeOne(self, *args, **kw):
        mtool = apply(MembershipTool, args, kw)
        return mtool.__of__(self.site)

    def test_MembersFolder_methods(self):
        mtool = self._makeOne()
        self.assertEqual( mtool.getMembersFolder(), None )
        self.site._setObject( 'Members', DummyFolder() )
        self.assertEqual( mtool.getMembersFolder(), self.site.Members )
        mtool.setMembersFolderById(id='foo')
        self.assertEqual( mtool.getMembersFolder(), None )
        self.site._setObject( 'foo', DummyFolder() )
        self.assertEqual( mtool.getMembersFolder(), self.site.foo )
        mtool.setMembersFolderById()
        self.assertEqual( mtool.getMembersFolder(), None )

    def test_interface(self):
        from Products.CMFDefault.interfaces.portal_membership \
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
