import unittest
import Zope

from Products.CMFCore.tests.base.testcase import RequestTest, SecurityTest

class FSPTMaker:

    def _makeOne( self, id, filename ):

        from Products.CMFCore.FSPageTemplate import FSPageTemplate
        from Products.CMFCore.tests.test_DirectoryView import skin_path_name
        from os.path import join

        return FSPageTemplate( id, join( skin_path_name, filename ) )

class FSPageTemplateTests( RequestTest, FSPTMaker ):

    def test_Call( self ):

        script = self._makeOne( 'testPT', 'testPT.pt' )
        script = script.__of__(self.root)
        self.assertEqual(script(),'foo\n')

    def test_BadCall( self ):

        from Products.PageTemplates.TALES import Undefined
        script = self._makeOne( 'testPTbad', 'testPTbad.pt' )
        script = script.__of__(self.root)
        self.assertRaises(Undefined,script)

class FSPageTemplateCustomizationTests( SecurityTest, FSPTMaker ):

    def setUp( self ):

        from OFS.Folder import Folder

        SecurityTest.setUp( self )

        self.root._setObject( 'portal_skins', Folder( 'portal_skins' ) )
        self.skins = self.root.portal_skins

        self.skins._setObject( 'custom', Folder( 'custom' ) )
        self.custom = self.skins.custom

        self.skins._setObject( 'fsdir', Folder( 'fsdir' ) )
        self.fsdir = self.skins.fsdir

        self.fsdir._setObject( 'testPT'
                             , self._makeOne( 'testPT', 'testPT.pt' ) )

        self.fsPT = self.fsdir.testPT

    def test_customize( self ):

        self.fsPT.manage_doCustomize( folder_path='custom' )

        self.assertEqual( len( self.custom.objectIds() ), 1 )
        self.failUnless( 'testPT' in self.custom.objectIds() )

    def test_dontExpandOnCreation( self ):

        self.fsPT.manage_doCustomize( folder_path='custom' )

        customized = self.custom.testPT
        self.failIf( customized.expand )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FSPageTemplateTests),
        unittest.makeSuite(FSPageTemplateCustomizationTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')




