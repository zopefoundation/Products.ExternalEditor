from unittest import makeSuite, main

from Products.CMFDefault.NewsItem import NewsItem

from Products.CMFCore.tests.base.testcase import RequestTest

from Products.CMFCore.tests.base.content import DOCTYPE
from Products.CMFCore.tests.base.content import BASIC_HTML
from Products.CMFCore.tests.base.content import ENTITY_IN_TITLE
from Products.CMFCore.tests.base.content import BASIC_STRUCTUREDTEXT

class NewsItemTests(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.d = NewsItem('foo')

    def test_Empty(self):
        d = NewsItem('foo', text_format='structured-text')
        assert d.title == ''
        assert d.description == ''
        assert d.text == ''
        assert d.text_format == 'structured-text'

    def test_BasicHtml(self):
        self.REQUEST['BODY']=BASIC_HTML
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Format() == 'text/html', d.Format()
        assert d.title == 'Title in tag'
        self.assertEqual(d.text.find('</body>'),-1)
        assert d.Description() == 'Describe me'
        self.assertEqual(len(d.Contributors()),3)

    def test_UpperedHtml(self):
        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Format() == 'text/html'
        assert d.title == 'TITLE IN TAG'
        self.assertEqual( d.text.find('</BODY'),-1)
        assert d.Description() == 'DESCRIBE ME'
        assert len(d.Contributors()) == 3

    def test_EntityInTitle(self):
        self.REQUEST['BODY'] = ENTITY_IN_TITLE
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.title == '&Auuml;rger', "Title '%s' being lost" % (
            d.title )

    def test_HtmlWithDoctype(self):
        d = self.d
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Description() == 'Describe me'

    def test_HtmlWithoutNewlines(self):
        d = self.d
        self.REQUEST['BODY'] = ''.join(BASIC_HTML.split('\n'))
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Format() == 'text/html'
        assert d.Description() == 'Describe me'

    def test_StructuredText(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        
        assert d.Format() == 'text/plain'
        self.assertEqual(d.Title(),'My Document')
        self.assertEqual(d.Description(),'A document by me')
        assert len(d.Contributors()) == 3
        self.failUnless(d.cooked_text.find('<p>') >= 0)

    def test_Init(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = NewsItem('foo', text='')
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Format() == 'text/plain'
        self.assertEqual(d.Title(),'My Document')
        self.assertEqual(d.Description(),'A document by me')
        assert len(d.Contributors()) == 3
        self.failUnless(d.cooked_text.find('<p>') >= 0)

        d = NewsItem('foo', text='')
        self.REQUEST['BODY'] = BASIC_HTML
        d.PUT(self.REQUEST, self.RESPONSE)
        assert d.Format() == 'text/html'
        assert d.Title() == 'Title in tag'
        assert len(d.Contributors()) == 3

        d = NewsItem('foo', text_format='structured-text', title='Foodoc')
        assert d.text == ''
        assert d.title == 'Foodoc'
        assert d.Format() == 'text/plain'

def test_suite():
    return makeSuite(NewsItemTests)

if __name__=='__main__':
    main(defaultTest='test_suite')
