from unittest import makeSuite, main

from Products.CMFDefault.NewsItem import NewsItem

from Products.CMFCore.tests.base.testcase import RequestTest

from Products.CMFCore.tests.base.content import DOCTYPE
from Products.CMFCore.tests.base.content import BASIC_HTML
from Products.CMFCore.tests.base.content import ENTITY_IN_TITLE
from Products.CMFCore.tests.base.content import BASIC_STRUCTUREDTEXT

class NewsItemTests(RequestTest):

    def test_Empty_html(self):

        d = NewsItem( 'empty', text_format='html' )

        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text, '' )

    def test_Empty_stx(self):

        d = NewsItem('foo', text_format='structured-text')

        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d.text, '' )

    def test_PUT_basic_html(self):

        self.REQUEST['BODY']=BASIC_HTML
        d = NewsItem('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_uppered_html(self):

        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = NewsItem('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'TITLE IN TAG' )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</BODY'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_entity_in_title(self):

        self.REQUEST['BODY'] = ENTITY_IN_TITLE
        d = NewsItem('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), '&Auuml;rger' )

    def test_PUT_html_with_doctype(self):

        d = NewsItem('foo')
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Description(), 'Describe me' )

    def test_PUT_html_without_newlines(self):

        d = NewsItem('foo')
        self.REQUEST['BODY'] = ''.join(BASIC_HTML.split('\n'))
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_PUT_structured_text(self):

        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = NewsItem('foo')
        d.PUT( self.REQUEST, self.RESPONSE )
        
        self.assertEqual( d.Title(), 'My Document')
        self.assertEqual( d.Description(), 'A document by me')
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

    def test_Init(self):

        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = NewsItem('foo', text='')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

    def test_Init_with_stx( self ):

        d = NewsItem('foo', text_format='structured-text', title='Foodoc')

        self.assertEqual( d.Title(), 'Foodoc' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d.text, '' )

def test_suite():
    return makeSuite(NewsItemTests)

if __name__=='__main__':
    main(defaultTest='test_suite')
