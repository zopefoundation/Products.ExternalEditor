from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.PortalContent import PortalContent


class PortalContentTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish

        verifyClass(IDynamicType, PortalContent)
        verifyClass(IContentish, PortalContent)


def test_suite():
    return TestSuite((
        makeSuite( PortalContentTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
