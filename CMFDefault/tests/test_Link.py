import unittest, string
from Products.CMFDefault.Link import Link

BASIC_STRUCTUREDTEXT = '''\
Title: Zope Community
Description: Link to the Zope Community website.
Subject: open source; Zope; community

http://www.zope.org
'''

class LinkTests(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty( self ):
        d = Link( 'foo' )
        self.failUnless( d.Title() == '' )
        self.failUnless( d.Description() == '' )
        self.failUnless( d.getRemoteUrl() == '' )

    def test_StructuredText( self ):
        d = Link('foo')
        d._writeFromPUT( body=BASIC_STRUCTUREDTEXT )
        
        self.failUnless( d.Title() == 'Zope Community' )
        self.failUnless(
                d.Description() == 'Link to the Zope Community website.' )
        self.failUnless( len(d.Subject()) == 3 )
        self.failUnless( d.getRemoteUrl() == 'http://www.zope.org' )

    def test_fixupMissingScheme( self ):
        d = Link( 'foo' )
        d.edit( 'http://foo.com' )
        self.failUnless( d.getRemoteUrl() == 'http://foo.com' )

        d = Link( 'bar' )
        d.edit( '//bar.com' )
        self.failUnless( d.getRemoteUrl() == 'http://bar.com' )

        d = Link( 'baz' )
        d.edit( 'baz.com' )
        self.failUnless( d.getRemoteUrl() == 'http://baz.com' )



def test_suite():
    return unittest.makeSuite(LinkTests)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__': main()
