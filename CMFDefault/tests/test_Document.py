import unittest, string
from Products.CMFDefault.Document import Document
#" 
DOCTYPE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'''

BASIC_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com baz@bam.net">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
  <meta name="keywords" content="unit tests, framework; ,zope ">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

ENTITY_IN_TITLE = '''\
<html>
 <head>
  <title>&Auuml;rger</title>
 </head>
 <bOdY>
  <h2>Not a lot here either</h2>
 </bodY>
</html>
'''

BASIC_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com baz@bam.net no@yes.maybe

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

STX_WITH_HTML = """\
Sometimes people do interesting things

  Sometimes people do interesting things like have examples
  of HTML inside their structured text document.  We should
  be detecting that this is indeed a structured text document
  and **NOT** an HTML document::

    <html>
    <head><title>Hello World</title></head>
    <body><p>Hello world, I am Bruce.</p></body>
    </html>

  All in favor say pi!
"""

class DocumentTests(unittest.TestCase):

    def test_Empty(self):
        d = Document('foo')
        assert d.title == ''
        assert d.description == ''
        assert d.text == ''
        assert d.text_format == 'structured-text'

    def test_BasicHtml(self):
        d = Document('foo', text=BASIC_HTML)
        assert d.Format() == 'text/html'
        assert d.title == 'Title in tag'
        assert string.find(d.text, '</body>') == -1
        assert d.Description() == 'Describe me'
        assert len(d.Contributors()) == 2

        subj = list(d.Subject())
        assert len(subj) == 4
        subj.sort()
        assert subj == [
            'content management',
            'framework',
            'unit tests',
            'zope'
            ]

    def test_UpperedHtml(self):
        d = Document('foo')
        d.edit(text_format='', text=string.upper(BASIC_HTML))
        assert d.Format() == 'text/html'
        assert d.title == 'TITLE IN TAG'
        assert string.find(d.text, '</BODY') == -1
        assert d.Description() == 'DESCRIBE ME'
        assert len(d.Contributors()) == 2

    def test_EntityInTitle(self):
        d = Document('foo')
        d.edit(text_format='html', text=ENTITY_IN_TITLE)
        assert d.title == '&Auuml;rger', "Title '%s' being lost" % (
            d.title )

    def test_HtmlWithDoctype(self):
        d = Document('foo')
        html = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.edit(text_format='', text=html)
        assert d.Description() == 'Describe me'

    def test_HtmlWithoutNewlines(self):
        d = Document('foo')
        html = string.join(string.split(BASIC_HTML, '\n'), '')
        d.edit(text_format='', text=html)
        assert d.Format() == 'text/html'
        assert d.Description() == 'Describe me'

    def test_StructuredText(self):
        d = Document('foo')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0

        # Make sure extra HTML is NOT found
        assert string.find(d.cooked_text, '<title>') == -1, d.cooked_text
        assert string.find(d.cooked_text, '<body>') == -1, d.cooked_text

    def test_Init(self):
        d = Document('foo', text=BASIC_STRUCTUREDTEXT)
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0

        d = Document('foo', text=BASIC_HTML)
        assert d.Format() == 'text/html'
        assert d.Title() == 'Title in tag'
        assert len(d.Contributors()) == 2

        d = Document('foo', title='Foodoc')
        assert d.text == ''
        assert d.title == 'Foodoc'
        assert d.Format() == 'text/plain'


class TestDocumentPUT(unittest.TestCase):
    def setUp(self):
        class Request:
            body = ''
            def get_header(self, h, d=''): return d
            def get(self, *args): return self.body
        class Response:
            status = 0
            def setHeader(self, *args): pass
            def setStatus(self, status): self.status = status
        self._request, self._response = Request(), Response()

    def tearDown(self):
        del self._response
        del self._request

    def test_PutStructuredTextWithHTML(self):
        d = Document('foo')
            
        self._request.body = STX_WITH_HTML

        r = d.PUT(self._request, self._response)
        assert d.Format() == 'text/plain', "%s != %s" % (
            d.Format(), 'text/plain')
        assert r.status == 204

    def test_PutStructuredText(self):
        d = Document('foo')

        self._request.body = BASIC_STRUCTUREDTEXT

        r = d.PUT(self._request, self._response)
        assert d.Format() == 'text/plain', '%s != %s' % (
            d.Format(), 'text/plain')
        assert r.status == 204

    def test_PutHtmlWithDoctype(self):
        d = Document('foo')
        html = '%s\n\n  \n   %s' % (DOCTYPE, BASIC_HTML)
        self._request.body = html
        r = d.PUT(self._request, self._response)
        assert d.Format() == 'text/html', "%s != %s" % (
            d.Format(), 'text/html')
        assert d.Description() == 'Describe me'
        assert r.status == 204

    def test_PutHtml(self):
        d = Document('foo')
        self._request.body = BASIC_HTML
        r = d.PUT(self._request, self._response)
        assert d.Format() == 'text/html', "%s != %s" % (
            d.Format(), 'text/html')
        assert d.Description() == 'Describe me'
        assert r.status == 204


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTests))
    suite.addTest(unittest.makeSuite(TestDocumentPUT))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

