import unittest, string, re
from Products.CMFDefault.tests.utils import fakeRequest, fakeResponse
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

STX_NO_HEADERS_BUT_COLON = """\
Plain STX:  No magic!

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""

class DocumentTests(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty(self):
        d = Document('foo', text_format='structured-text')
        self.assertEqual( d.title, '' )
        self.assertEqual( d.description, '' )
        self.assertEqual( d.text, '' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d._stx_level, 1 )

    def test_BasicHtmlPUT(self):
        REQUEST = fakeRequest()
        REQUEST['BODY'] = BASIC_HTML
        d = Document('foo')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'Title in tag' )
        self.assertEqual( string.find(d.text, '</body>'), -1 )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.assertEqual( d.Contributors()[-1], 'Benotz, Larry J (larry@benotz.stuff)' )

        # Since the format is html, the STX level operands should
        # have no effect.
        ct = d.CookedBody(stx_level=3, setlevel=1)
        self.assertEqual( d._stx_level, 1 )

        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_UpperedHtml(self):
        REQUEST=fakeRequest()
        REQUEST['BODY'] = string.upper(BASIC_HTML)
        d = Document('foo')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'TITLE IN TAG' )
        self.assertEqual( string.find(d.text, '</BODY'), -1 )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_EntityInTitle(self):
        REQUEST=fakeRequest()
        REQUEST['BODY'] = ENTITY_IN_TITLE 
        d = Document('foo')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.title, '&Auuml;rger' )

    def test_HtmlWithDoctype(self):
        REQUEST=fakeRequest()
        d = Document('foo')
        REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Description(), 'Describe me' )

    def test_HtmlWithoutNewlines(self):
        REQUEST=fakeRequest()
        d = Document('foo')
        REQUEST['BODY'] = string.join(string.split(BASIC_HTML, '\n'), '')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )

    def test_BigHtml(self):
        REQUEST = fakeRequest()
        d = Document('foo')
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % string.join(s, '\n')
        REQUEST['BODY'] = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.CookedBody(), body )

    def test_BigHtml_via_upload(self):
        d = Document('foo')
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % string.join(s, '\n')
        html = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        from StringIO import StringIO
        file = StringIO( html )
        d.edit(text_format='html', text='', file=file)
        self.assertEqual( d.CookedBody(), body )
        

    def test_EditStructuredTextWithHTML(self):
        d = Document('foo')
        d.edit(text_format='structured-text', text=STX_WITH_HTML)
        
        self.assertEqual( d.Format(), 'text/plain' )

    def test_StructuredText(self):
        REQUEST=fakeRequest()
        REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = Document('foo')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( string.find(d.cooked_text, '<p>') >= 0 )
        self.failUnless( string.find(d.CookedBody(), '<h1') >= 0 )

        # Make sure extra HTML is NOT found
        self.failUnless( string.find(d.cooked_text, '<title>') < 0 )
        self.failUnless( string.find(d.cooked_text, '<body>') < 0 )

        # test subject/keyword headers
        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_STX_Levels(self):
        d = Document('foo')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody()
        self.failUnless( string.find(d.CookedBody(), '<h1') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2)
        self.failIf( (string.find(ct, '<h1') >= 0) )
        self.failUnless( string.find(ct, '<h2') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2, setlevel=1)
        self.failIf( (string.find(ct, '<h1') >= 0) )
        self.failUnless( string.find(ct, '<h2') >= 0 )
        self.assertEqual( d._stx_level, 2 )

        ct = d.CookedBody()
        self.assertEqual( d._stx_level, 2 )
        self.failIf( (string.find(d.CookedBody(), '<h1') >= 0) )
        self.failUnless( string.find(d.CookedBody(), '<h2') >= 0 )

    def test_Init(self):
        REQUEST=fakeRequest()
        REQUEST['BODY']=BASIC_STRUCTUREDTEXT
        d = Document('foo')
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( string.find(d.cooked_text, '<p>') >= 0 )

        d = Document('foo', text='')
        REQUEST['BODY']=BASIC_HTML
        d.PUT(REQUEST, RESPONSE=fakeResponse())
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( len(d.Contributors()), 3 )

        d = Document('foo', text_format='structured-text', title='Foodoc')
        self.assertEqual( d.text, '' )
        self.failIf( d.CookedBody() )
        self.assertEqual( d.title, 'Foodoc' )
        self.assertEqual( d.Format(), 'text/plain' )

        # Tracker issue 435:  initial text is not cooked.
        d = Document('foo', text_format='structured-text', text=STX_NO_HEADERS)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS )
        self.failUnless( d.CookedBody() )
        self.assertEqual( d.Format(), 'text/plain' )
    
    def test_STX_NoHeaders( self ):
        REQUEST=fakeRequest()
        REQUEST['BODY']=STX_NO_HEADERS
        d = Document('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )

        d.PUT(REQUEST, RESPONSE=fakeResponse())
        
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )
    
    def test_STX_NoHeaders_but_colon( self ):
        d = Document('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.edit(text_format='structured-text', text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )
    
    def test_ZMI_edit( self ):
        d = Document('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.manage_editDocument( text_format='structured-text'
                             , text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )


class TestFTPGet( unittest.TestCase ):

    def testHTML( self ):
        REQUEST=fakeRequest()
        REQUEST['BODY']=SIMPLE_HTML
        d = Document( 'foo' )
        d.PUT(REQUEST, RESPONSE=fakeResponse())

        rnlinesplit = re.compile( r'\r?\n?' )
        simple_lines = rnlinesplit.split( SIMPLE_HTML )
        get_lines = rnlinesplit.split( d.manage_FTPget() )

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

        self.assertEqual( get_lines, simple_lines )

        self.failUnless( get_headers )
        self.failUnless( simple_headers )
        self.failUnless( len( get_headers ) >= len( simple_headers ) )

        for header in simple_headers:
            self.failUnless( header in get_headers )

    def testSTX( self ):
        REQUEST=fakeRequest()
        REQUEST['BODY']=SIMPLE_STRUCTUREDTEXT
        d = Document( 'foo' )
        d.PUT(REQUEST, RESPONSE=fakeResponse())

        rnlinesplit = re.compile( r'\r?\n?' )

        get_text = d.manage_FTPget()
        simple_lines = rnlinesplit.split( SIMPLE_STRUCTUREDTEXT )
        get_lines = rnlinesplit.split( get_text )

        # strip off headers
        simple_headers = []
        while simple_lines and simple_lines[0]:
            simple_headers.append( simple_lines[0] )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0]:
            get_headers.append( get_lines[0] )
            get_lines = get_lines[1:]

        self.assertEqual( get_lines, simple_lines )

        for header in simple_headers:
            self.failUnless( header in get_headers )

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
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutStructuredText(self):
        d = Document('foo')

        self._request.body = BASIC_STRUCTUREDTEXT

        r = d.PUT(self._request, self._response)
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutHtmlWithDoctype(self):
        d = Document('foo')
        html = '%s\n\n  \n   %s' % (DOCTYPE, BASIC_HTML)
        self._request.body = html
        r = d.PUT(self._request, self._response)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )

    def test_PutHtml(self):
        d = Document('foo')
        self._request.body = BASIC_HTML
        r = d.PUT(self._request, self._response)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )


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

