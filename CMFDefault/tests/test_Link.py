from unittest import TestCase, TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from re import compile

from Products.CMFCore.tests.base.content import BASIC_RFC822
from Products.CMFCore.tests.base.content import RFC822_W_CONTINUATION
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFDefault.Link import Link


class LinkTests(TestCase):

    def setUp(self):
        self.site = DummySite('site')
        mtool = self.site._setObject( 'portal_membership', DummyTool() )

    def _makeOne(self, id, *args, **kw):
        return self.site._setObject( id, Link(id, *args, **kw) )

    def canonTest(self, table):
        for orig, wanted in table.items():
            # test with constructor
            d = self._makeOne('foo', remote_url=orig)
            self.assertEqual(d.getRemoteUrl(), wanted)
            # test with edit method too
            d = self._makeOne('bar')
            d.edit(orig)
            self.assertEqual(d.getRemoteUrl(), wanted)

    def test_Empty( self ):
        d = Link( 'foo' )
        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.getRemoteUrl(), '' )
        self.assertEqual( d.format, 'text/url' )
        self.assertEqual( d.URL_FORMAT, 'text/url')

        d = self._makeOne('foo', remote_url='bar')
        d.edit('')
        self.assertEqual(d.getRemoteUrl(), '')

        d = self._makeOne('foo', remote_url='http://')
        self.assertEqual(d.getRemoteUrl(), '')

        d = self._makeOne('foo', remote_url='http:')
        self.assertEqual(d.getRemoteUrl(), '')

    def test_RFC822(self):
        d = self._makeOne('foo')
        d._writeFromPUT( body=BASIC_RFC822 )

        self.assertEqual( d.Title(), 'Zope Community' )
        self.assertEqual( d.Description()
                        , 'Link to the Zope Community website.' )
        self.assertEqual( len(d.Subject()), 3 )
        self.assertEqual( d.getRemoteUrl(), 'http://www.zope.org' )

    def test_RFC822_w_Continuation(self):
        d = self._makeOne('foo')
        d._writeFromPUT( body=RFC822_W_CONTINUATION )
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
