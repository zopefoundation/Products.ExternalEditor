from unittest import TestCase, TestSuite, makeSuite, main

import Zope

from Products.CMFCore.tests.base.dummy import DummyFolder as BaseDummyFolder
from Products.CMFCore.tests.base.dummy import DummyContent

from Products.CMFCore.URLTool import URLTool


class DummyFolder(BaseDummyFolder):

    def __init__(self, id='', fake_product=0, prefix=''):
        BaseDummyFolder.__init__(self, fake_product, prefix)
        self._id = id

    def getId(self):
        return self._id

    def getPhysicalPath(self):
        return self.aq_inner.aq_parent.getPhysicalPath() + ( self._id, )


class DummySite(DummyFolder):

    _domain = 'http://www.foobar.com'
    _path = 'bar'

    def absolute_url(self, relative=0):
        return '/'.join( (self._domain, self._path, self._id) )

    def getPhysicalPath(self):
        return ('', self._path, self._id)


class URLToolTests(TestCase):

    def setUp(self):
        self.site = DummySite(id='foo')

    def _makeOne(self, *args, **kw):
        url_tool = apply( URLTool, args, kw )
        return url_tool.__of__( self.site )

    def test_portal_methods(self):
        url_tool = self._makeOne()
        self.assertEqual( url_tool()
                        , 'http://www.foobar.com/bar/foo' )
        self.assertEqual( url_tool.getPortalObject()
                        , self.site )
        self.assertEqual( url_tool.getPortalPath()
                        , '/bar/foo' )

    def test_content_methods(self):
        url_tool = self._makeOne()
        self.site._setObject( 'folder', DummyFolder(id='buz') )
        self.site.folder._setObject( 'item', DummyContent(id='qux.html') )
        obj = self.site.folder.item
        self.assertEqual( url_tool.getRelativeContentPath(obj)
                        , ('buz', 'qux.html') )
        self.assertEqual( url_tool.getRelativeContentURL(obj)
                        , 'buz/qux.html' )
        self.assertEqual( url_tool.getRelativeUrl(obj)
                        , 'buz/qux.html' )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_url \
                import portal_url as IURLTool
        try:
            from Interface.Verify import verifyClass
        except ImportError:
            # for Zope versions before 2.6.0
            from Interface import verify_class_implementation as verifyClass

        verifyClass(IURLTool, URLTool)


def test_suite():
    return TestSuite((
        makeSuite( URLToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
