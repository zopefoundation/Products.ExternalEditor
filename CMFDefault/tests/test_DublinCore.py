from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl


class DublinCoreTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore

        verifyClass(IDublinCore, DefaultDublinCoreImpl)
        verifyClass(ICatalogableDublinCore, DefaultDublinCoreImpl)
        verifyClass(IMutableDublinCore, DefaultDublinCoreImpl)


def test_suite():
    return TestSuite((
        makeSuite( DublinCoreTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
