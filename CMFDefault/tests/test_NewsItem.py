from unittest import TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from Products.CMFCore.tests.base.content import DOCTYPE
from Products.CMFCore.tests.base.content import BASIC_HTML
from Products.CMFCore.tests.base.content import ENTITY_IN_TITLE
from Products.CMFCore.tests.base.content import BASIC_STRUCTUREDTEXT
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.testcase import RequestTest
from Products.CMFDefault.NewsItem import NewsItem


class NewsItemTests(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.site._setObject( 'portal_membership', DummyTool() )

    def _makeOne(self, id, *args, **kw):
        return self.site._setObject( id, NewsItem(id, *args, **kw) )

    def test_Empty_html(self):
        d = self._makeOne('empty', text_format='html')

        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text, '' )

    def test_Empty_stx(self):
        d = self._makeOne('foo', text_format='structured-text')

        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d.text, '' )

    def test_PUT_basic_html(self):
        self.REQUEST['BODY']=BASIC_HTML
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_uppered_html(self):
        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'TITLE IN TAG' )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</BODY'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_entity_in_title(self):
        self.REQUEST['BODY'] = ENTITY_IN_TITLE
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), '&Auuml;rger' )

    def test_PUT_html_with_doctype(self):
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Description(), 'Describe me' )

    def test_PUT_html_without_newlines(self):
        self.REQUEST['BODY'] = ''.join(BASIC_HTML.split('\n'))
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_structured_text(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self._makeOne('foo')
        d.PUT( self.REQUEST, self.RESPONSE )

        self.assertEqual( d.Title(), 'My Document')
        self.assertEqual( d.Description(), 'A document by me')
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

    def test_Init(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self._makeOne('foo', text='')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

    def test_Init_with_stx( self ):
        d = self._makeOne('foo', text_format='structured-text',
                          title='Foodoc')

        self.assertEqual( d.Title(), 'Foodoc' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d.text, '' )


def test_suite():
    return TestSuite((
        makeSuite(NewsItemTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
