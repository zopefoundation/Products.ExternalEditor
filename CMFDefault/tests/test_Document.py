from unittest import TestSuite, makeSuite, main
from StringIO import StringIO
from re import compile

from Products.CMFCore.tests.base.testcase import RequestTest

from Products.CMFCore.tests.base.content import DOCTYPE
from Products.CMFCore.tests.base.content import HTML_TEMPLATE
from Products.CMFCore.tests.base.content import BASIC_HTML
from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import ENTITY_IN_TITLE
from Products.CMFCore.tests.base.content import BASIC_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import STX_WITH_HTML
from Products.CMFCore.tests.base.content import STX_NO_HEADERS
from Products.CMFCore.tests.base.content import STX_NO_HEADERS_BUT_COLON
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML

from Products.CMFDefault.Document import Document

class DocumentTests(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.d = Document('foo')

    def test_Empty(self):
        d = Document('foo', text_format='structured-text')
        self.assertEqual( d.title, '' )
        self.assertEqual( d.description, '' )
        self.assertEqual( d.text, '' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d._stx_level, 1 )

    def test_BasicHtmlPUT(self):
        self.REQUEST['BODY'] = BASIC_HTML
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'Title in tag' )
        self.assertEqual( d.text.find('</body>'), -1 )
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
        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'TITLE IN TAG' )
        self.assertEqual( d.text.find('</BODY'), -1 )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_EntityInTitle(self):
        self.REQUEST['BODY'] = ENTITY_IN_TITLE 
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.title, '&Auuml;rger' )

    def test_HtmlWithDoctype(self):
        d = self.d
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Description(), 'Describe me' )

    def test_HtmlWithoutNewlines(self):
        d = self.d
        self.REQUEST['BODY'] = ''.join((BASIC_HTML.split('\n')))
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )

    def test_EditStripHTMLToBody(self):
        # bodyfind should strip away everything but the contents of the body
        # tag.
        self.REQUEST['BODY'] = BASIC_HTML
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEquals(d.cooked_text, '\n  <h1>Not a lot here</h1>\n ')

    def test_EditPlainDocumentWithEmbeddedHTML(self):
        d = self.d
        d.edit('structured-text', FAUX_HTML_LEADING_TEXT)
        fully_edited = d.cooked_text
        d._edit(FAUX_HTML_LEADING_TEXT, 'structured-text')
        partly_edited = d.cooked_text
        self.assertEquals(fully_edited, partly_edited)

    def test_BigHtml(self):
        d = self.d
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        self.REQUEST['BODY'] = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.CookedBody(), body )

    def test_BigHtml_via_upload(self):
        d = self.d
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        html = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        file = StringIO( html )
        d.edit(text_format='html', text='', file=file)
        self.assertEqual( d.CookedBody(), body )
        
    def test_plain_text(self):
        """test that plain text forrmat works"""
        d = self.d 
        d.edit(text_format='plain', text='*some plain text*\nwith a newline')
        self.assertEqual( d.CookedBody(), '*some plain text*<br>with a newline')

    def test_EditStructuredTextWithHTML(self):
        d = self.d
        d.edit(text_format='structured-text', text=STX_WITH_HTML)
        
        self.assertEqual( d.Format(), 'text/plain' )

    def test_StructuredText(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )
        self.failUnless( d.CookedBody().find('<h1') >= 0 )

        # Make sure extra HTML is NOT found
        self.failUnless( d.cooked_text.find('<title>') < 0 )
        self.failUnless( d.cooked_text.find('<body>') < 0 )

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
        d = self.d
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody()
        self.failUnless( d.CookedBody().find('<h1') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2, setlevel=1)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 2 )

        ct = d.CookedBody()
        self.assertEqual( d._stx_level, 2 )
        self.failIf( d.CookedBody().find('<h1') >= 0 )
        self.failUnless( d.CookedBody().find('<h2') >= 0 )

    def test_Init(self):
        self.REQUEST['BODY']=BASIC_STRUCTUREDTEXT
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

        d = Document('foo', text='')
        self.REQUEST['BODY']=BASIC_HTML
        d.PUT(self.REQUEST, self.RESPONSE)
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
        self.REQUEST['BODY']=STX_NO_HEADERS
        d = self.d
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

        d.PUT(self.REQUEST, self.RESPONSE)
        
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )
    
    def test_STX_NoHeaders_but_colon( self ):
        d = self.d
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.edit(text_format='structured-text', text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )
    
    def test_ZMI_edit( self ):
        d = self.d
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.manage_editDocument( text_format='structured-text'
                             , text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )


class TestFTPGet( RequestTest ):

    def testHTML( self ):
        self.REQUEST['BODY']=BASIC_HTML
        d = Document( 'foo' )
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )
        simple_lines = rnlinesplit.split( BASIC_HTML )
        get_lines = rnlinesplit.split( d.manage_FTPget() )

        # strip off headers
        meta_pattern = compile( r'meta name="([a-z]*)" '
                                 + r'content="([a-z]*)"'
                                 )
        title_pattern = compile( r'<title>(.*)</title>' )
        simple_headers = []
        while simple_lines and simple_lines[0] != '<BODY>':
            header = simple_lines[0].strip().lower() 
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
            header = get_lines[0].strip().lower()
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
        self.REQUEST['BODY']=SIMPLE_STRUCTUREDTEXT
        d = Document( 'foo' )
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )

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

class TestDocumentPUT(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.d = Document('foo')

    def test_PutStructuredTextWithHTML(self):
            
        self.REQUEST['BODY'] = STX_WITH_HTML

        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutStructuredText(self):

        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT

        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutHtmlWithDoctype(self):
        
        html = '%s\n\n  \n   %s' % (DOCTYPE, BASIC_HTML)
        self.REQUEST['BODY'] = html
        
        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/html' )
        self.assertEqual( self.d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )

    def test_PutHtml(self):
        
        self.REQUEST['BODY'] = BASIC_HTML
        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/html' )
        self.assertEqual( self.d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )


def test_suite():
    return TestSuite((
        makeSuite(DocumentTests),
        makeSuite(TestFTPGet),
        makeSuite(TestDocumentPUT),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

