import unittest, string, re
from Products.CMFDefault.Document import Document
#" 
DOCTYPE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'''

HTML_TEMPLATE = '''\
<html><head>
 <title>%(title)s</title>
</head>
<body bgcolor="#efe843">%(body)s</body>
</html>
'''

BASIC_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
  <meta name="keywords" content="unit tests, framework; ,zope ">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

SIMPLE_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
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
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope
Keywords: unit tests; , framework

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

SIMPLE_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope

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

STX_NO_HEADERS = """\
Title Phrase

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""

class DocumentTests(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty(self):
        d = Document('foo')
        assert d.title == ''
        assert d.description == ''
        assert d.text == ''
        assert d.text_format == 'structured-text'
        assert d._stx_level == 1

    def test_BasicHtml(self):
        d = Document('foo', text=BASIC_HTML)
        assert d.Format() == 'text/html'
        assert d.title == 'Title in tag'
        assert string.find(d.text, '</body>') == -1
        assert d.Description() == 'Describe me'
        assert len(d.Contributors()) == 3
        assert d.Contributors()[-1] == 'Benotz, Larry J (larry@benotz.stuff)'

        # Since the format is html, the STX level operands should
        # have no effect.
        ct = d.CookedBody(stx_level=3, setlevel=1)
        assert d._stx_level == 1

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
        assert len(d.Contributors()) == 3

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

    def test_BigHtml(self):
        d = Document('foo')
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % string.join(s, '\n')
        html = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        d.edit(text_format=None, text=html)
        assert d.CookedBody() == body
        

    def test_EditStructuredTextWithHTML(self):
        d = Document('foo')
        d.edit(text_format=None, text=STX_WITH_HTML)
        
        assert d.Format() == 'text/plain', "%s != %s" % (
            d.Format(), 'text/plain')

    def test_StructuredText(self):
        d = Document('foo')
        assert hasattr(d, 'cooked_text')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0
        assert string.find(d.CookedBody(), '<h1') >= 0

        # Make sure extra HTML is NOT found
        assert string.find(d.cooked_text, '<title>') == -1, d.cooked_text
        assert string.find(d.cooked_text, '<body>') == -1, d.cooked_text

        # test subject/keyword headers
        subj = list(d.Subject())
        assert len(subj) == 4
        subj.sort()
        assert subj == [
            'content management',
            'framework',
            'unit tests',
            'zope'
            ]

    def test_STX_Levels(self):
        d = Document('foo', text=BASIC_STRUCTUREDTEXT)
        assert d._stx_level == 1

        ct = d.CookedBody()
        assert string.find(d.CookedBody(), '<h1') >= 0
        assert d._stx_level == 1

        ct = d.CookedBody(stx_level=2)
        assert not (string.find(ct, '<h1') >= 0)
        assert string.find(ct, '<h2') >= 0
        assert d._stx_level == 1

        ct = d.CookedBody(stx_level=2, setlevel=1)
        assert not (string.find(ct, '<h1') >= 0)
        assert string.find(ct, '<h2') >= 0
        assert d._stx_level == 2

        ct = d.CookedBody()
        assert d._stx_level == 2
        assert not (string.find(d.CookedBody(), '<h1') >= 0)
        assert string.find(d.CookedBody(), '<h2') >= 0

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
        assert len(d.Contributors()) == 3

        d = Document('foo', title='Foodoc')
        assert d.text == ''
        assert d.title == 'Foodoc'
        assert d.Format() == 'text/plain'
    
    def test_STX_NoHeaders( self ):
        d = Document('foo')
        d._editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )
        assert d.Format() == 'text/html'
        assert d.Title() == 'Plain STX'
        assert d.Description() == 'Look, Ma, no headers!'
        assert len( d.Subject() ) == 2
        assert 'plain' in d.Subject()
        assert 'STX' in d.Subject()

        d.edit(text_format='structured-text', text=STX_NO_HEADERS)
        
        assert d.Format() == 'text/plain'
        assert d.Title() == 'Plain STX'
        assert d.Description() == 'Look, Ma, no headers!'
        assert len( d.Subject() ) == 2
        assert 'plain' in d.Subject()
        assert 'STX' in d.Subject()


class TestFTPGet( unittest.TestCase ):

    def testHTML( self ):
        d = Document( 'foo' )
        d._edit( text_format="html", text=SIMPLE_HTML )

        simple_lines = string.split( SIMPLE_HTML, '\n' )
        get_lines = string.split( d.manage_FTPget(), '\n' )

        # strip off headers
        meta_pattern = re.compile( r'meta name="([a-z]*)" '
                                 + r'content="([a-z]*)"'
                                 )
        title_pattern = re.compile( r'<title>(.*)</title>' )
        simple_headers = []
        while simple_lines and simple_lines[0] != '<BODY>':
            header = string.lower( string.strip( simple_lines[0] ) ) 
            match = meta_pattern.search( header )
            if match:
                simple_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    simple_headers.append( ( 'title', match.group(1) ) )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0] != '<BODY>':
            header = string.lower( string.strip( get_lines[0] ) ) 
            match = meta_pattern.search( header )
            if match:
                get_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    get_headers.append( ( 'title', match.group(1) ) )
            get_lines = get_lines[1:]

        assert get_lines == simple_lines

        assert get_headers
        assert simple_headers
        assert len( get_headers ) >= len( simple_headers )

        for header in simple_headers:
            assert header in get_headers, [header, get_headers]

    def testSTX( self ):
        d = Document( 'foo' )
        d._edit( text_format="structured-text", text=SIMPLE_STRUCTUREDTEXT )

        simple_lines = string.split( SIMPLE_STRUCTUREDTEXT, '\n' )
        get_lines = string.split( d.manage_FTPget(), '\n' )

        # strip off headers
        simple_headers = []
        while simple_lines and simple_lines[0]:
            simple_headers.append( simple_lines[0] )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0]:
            get_headers.append( get_lines[0] )
            get_lines = get_lines[1:]

        assert get_lines == simple_lines

        for header in simple_headers:
            assert header in get_headers, [header, get_headers]

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
    suite.addTest(unittest.makeSuite(TestFTPGet))
    suite.addTest(unittest.makeSuite(TestDocumentPUT))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

