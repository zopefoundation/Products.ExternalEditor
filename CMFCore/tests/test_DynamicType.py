from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.DynamicType import DynamicType


class DynamicTypeTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType

        verifyClass(IDynamicType, DynamicType)


def test_suite():
    return TestSuite((
        makeSuite( DynamicTypeTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
