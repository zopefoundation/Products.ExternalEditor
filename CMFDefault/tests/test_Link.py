import unittest, string
from Products.CMFDefault.Link import Link

BASIC_STRUCTUREDTEXT = '''\
Title: Zope Community
Description: Link to the Zope Community website.
Subject: open source; Zope; community

http://ww.zope.org
'''

class LinkTests(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_Empty(self):
        d = Link('foo')
        assert d.Title() == ''
        assert d.Description() == ''
        assert d.getRemoteUrl() == ''

    def test_StructuredText(self):
        d = Link('foo')
        d._writeFromPUT( body=BASIC_STRUCTUREDTEXT )
        
        assert d.Title() == 'Zope Community'
        assert d.Description() == 'Link to the Zope Community website.'
        assert len(d.Subject()) == 3


def test_suite():
    return unittest.makeSuite(LinkTests)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__': main()
