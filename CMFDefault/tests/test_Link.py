import unittest, string, re
from Products.CMFDefault.Link import Link

BASIC_STRUCTUREDTEXT = '''\
Title: Zope Community
Description: Link to the Zope Community website.
Subject: open source; Zope; community

http://www.zope.org
'''

STX_W_CONTINUATION = '''\
Title: Zope Community
Description: Link to the Zope Community website,
  including hundreds of contributed Zope products.
Subject: open source; Zope; community

http://www.zope.org
'''

class LinkTests(unittest.TestCase):

    def test_Empty( self ):
        d = Link( 'foo' )
        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.getRemoteUrl(), '' )
        self.assertEqual( d.format, 'text/url' )
        self.assertEqual( d.URL_FORMAT, 'text/url')

    def test_StructuredText( self ):
        d = Link('foo')
        d._writeFromPUT( body=BASIC_STRUCTUREDTEXT )
        
        self.assertEqual( d.Title(), 'Zope Community' )
        self.assertEqual( d.Description()
                        , 'Link to the Zope Community website.' )
        self.assertEqual( len(d.Subject()), 3 )
        self.assertEqual( d.getRemoteUrl(), 'http://www.zope.org' )

    def test_StructuredText_w_Continuation( self ):

        d = Link('foo')
        d._writeFromPUT( body=STX_W_CONTINUATION )
        rnlinesplit = re.compile( r'\r?\n?' )
        desc_lines = rnlinesplit.split( d.Description() )
        
        self.assertEqual( d.Title(), 'Zope Community' )
        self.assertEqual( desc_lines[0]
                        , 'Link to the Zope Community website,' )
        self.assertEqual( desc_lines[1]
                        , 'including hundreds of contributed Zope products.' )
        self.assertEqual( len(d.Subject()), 3 )
        self.assertEqual( d.getRemoteUrl(), 'http://www.zope.org' )

    def test_fixupMissingScheme( self ):
        d = Link( 'foo' )
        d.edit( 'http://foo.com' )
        self.assertEqual( d.getRemoteUrl(), 'http://foo.com' )

        d = Link( 'bar' )
        d.edit( '//bar.com' )
        self.assertEqual( d.getRemoteUrl(), 'http://bar.com' )

        d = Link( 'baz' )
        d.edit( 'baz.com' )
        self.assertEqual( d.getRemoteUrl(), 'http://baz.com' )



def test_suite():
    return unittest.makeSuite(LinkTests)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__': main()
