import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from re import compile

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

class LinkTests(TestCase):

    def canonTest(self, table):
        for orig, wanted in table.items():
            # test with constructor
            d = Link('foo', remote_url=orig)
            self.assertEqual(d.getRemoteUrl(), wanted)
            # test with edit method too
            d = Link('bar')
            d.edit(orig)
            self.assertEqual(d.getRemoteUrl(), wanted)

    def test_Empty( self ):
        d = Link( 'foo' )
        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.getRemoteUrl(), '' )
        self.assertEqual( d.format, 'text/url' )
        self.assertEqual( d.URL_FORMAT, 'text/url')

        d = Link('foo', remote_url='bar')
        d.edit('')
        self.assertEqual(d.getRemoteUrl(), '')

        d = Link('foo', remote_url='http://')
        self.assertEqual(d.getRemoteUrl(), '')

        d = Link('foo', remote_url='http:')
        self.assertEqual(d.getRemoteUrl(), '')

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
        rnlinesplit = compile( r'\r?\n?' )
        desc_lines = rnlinesplit.split( d.Description() )
        
        self.assertEqual( d.Title(), 'Zope Community' )
        self.assertEqual( desc_lines[0]
                        , 'Link to the Zope Community website,' )
        self.assertEqual( desc_lines[1]
                        , 'including hundreds of contributed Zope products.' )
        self.assertEqual( len(d.Subject()), 3 )
        self.assertEqual( d.getRemoteUrl(), 'http://www.zope.org' )

    def test_fixupMissingScheme(self):
        table = {
            'http://foo.com':      'http://foo.com',
            '//bar.com':           'http://bar.com',
            }
        self.canonTest(table)

    def test_keepRelativeUrl(self):
        table = {
            'baz.com':             'baz.com',
            'baz2.com/index.html': 'baz2.com/index.html',
            '/huh/zoinx.html':     '/huh/zoinx.html',
            'hmmm.com/lol.txt':    'hmmm.com/lol.txt',
            }
        self.canonTest(table)

    def test_trailingSlash(self):
        table = {
            'http://foo.com/bar/': 'http://foo.com/bar/',
            'baz.com/':            'baz.com/',
            '/baz.org/zoinx/':     '/baz.org/zoinx/',
            }
        self.canonTest(table)

    def test_otherScheme(self):
        table = {
            'mailto:user@foo.com':      'mailto:user@foo.com',
            'https://bank.com/account': 'https://bank.com/account',
            }
        self.canonTest(table)


def test_suite():
    return TestSuite((
        makeSuite(LinkTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
