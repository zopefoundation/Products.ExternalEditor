import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from test_DirectoryView import skin_path_name
from os.path import join
from Testing.makerequest import makerequest
from Products.PageTemplates.TALES import Undefined

class FSPageTemplateTests( TestCase ):

    def test_Call( self ):
        """
        Test calling works
        """
        root = makerequest(Zope.app())
        script = FSPageTemplate('testPT', join(skin_path_name,'testPT.pt'))
        script = script.__of__(root)
        self.assertEqual(script(),'foo\n')

    def test_BadCall( self ):
        """
        Test calling a bad template gives an Undefined exception
        """
        root = makerequest(Zope.app())
        script = FSPageTemplate('testPT', join(skin_path_name,'testPTbad.pt'))
        script = script.__of__(root)
        self.assertRaises(Undefined,script)

def test_suite():
    return TestSuite((
        makeSuite(FSPageTemplateTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()




