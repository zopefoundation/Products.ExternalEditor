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

from Acquisition import Implicit
from ZPublisher.BaseRequest import BaseRequest
from ZPublisher.HTTPResponse import HTTPResponse

from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool


class DummyContent(DynamicType, Implicit):
    """ Basic dynamic content class.
    """

    portal_type = 'Dummy Content 15'


class DynamicTypeTests(TestCase):

    def setUp(self):
        self.site = DummySite('site')
        self.ttool = self.site._setObject( 'portal_types', TypesTool() )
        fti = FTIDATA_CMF15[0].copy()
        self.ttool._setObject( 'Dummy Content 15', FTI(**fti) )
        self.foo = self.site._setObject( 'foo', DummyContent() )

    def test_getTypeInfo(self):
        self.assertEqual( self.foo.getTypeInfo().getId(), 'Dummy Content 15' )

    def test___before_publishing_traverse__(self):
        dummy_view = self.site._setObject( 'dummy_view', DummyObject() )
        response = HTTPResponse()
        environment = { 'URL': '',
                        'PARENTS': [self.site],
                        'REQUEST_METHOD': 'GET',
                        'steps': [],
                        '_hacked_path': 0,
                        'response': response }
        r = BaseRequest(environment)

        r.traverse('foo')
        self.assertEqual( r.URL, '/foo/dummy_view' )
        self.assertEqual( r.response.base, '/foo/',
                          'CMF Collector issue #192 (wrong base): %s'
                          % (r.response.base or 'empty',) )

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
