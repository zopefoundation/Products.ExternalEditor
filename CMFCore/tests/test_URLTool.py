from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.URLTool import URLTool


class URLToolTests(TestCase):

    def setUp(self):
        self.site = DummySite(id='foo')

    def _makeOne(self, *args, **kw):
        url_tool = URLTool(*args, **kw)
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
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IURLTool, URLTool)
        verifyClass(IActionProvider, URLTool)


def test_suite():
    return TestSuite((
        makeSuite( URLToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
