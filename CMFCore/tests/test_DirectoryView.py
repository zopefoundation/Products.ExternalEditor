import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.testcase import FSDVTest
from Products.CMFCore.tests.base.testcase import _prefix

from Globals import DevelopmentMode

from os import remove, mkdir, rmdir
from os.path import join

class DirectoryViewPathTests( TestCase ):
    """
    These test that, no matter what is stored in their dirpath,
    FSDV's will do their best to find an appropriate skin
    and only do nothing in difficult cases (such as where
    people have chosen to use PRODUCTS_PATH )
    """
    def setUp(self):
        from Products.CMFCore.DirectoryView import registerDirectory
        from Products.CMFCore.DirectoryView import addDirectoryViews
        registerDirectory('fake_skins', _prefix)
        self.ob = DummyFolder()
        addDirectoryViews(self.ob, 'fake_skins', _prefix)        
        
    def test_getDirectoryInfo1( self ):
        """ windows INSTANCE_HOME  """
        self.ob.fake_skin.manage_properties(r'Products\CMFCore\tests\fake_skins\fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo2( self ):
        """ windows SOFTWARE_HOME  """
        self.ob.fake_skin.manage_properties(r'C:\Zope\2.5.1\Products\CMFCore\tests\fake_skins\fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo3( self ):
        """ *nix INSTANCE_HOME  """
        self.ob.fake_skin.manage_properties('Products/CMFCore/tests/fake_skins/fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo5( self ):
        """ *nix SOFTWARE_HOME  """
        self.ob.fake_skin.manage_properties('/usr/local/zope/2.5.1/Products/CMFCore/tests/fake_skins/fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo5( self ):
        """ Somewhere we won't be able to find  """
        from tempfile import mktemp        
        self.ob.fake_skin.manage_properties(mktemp()+'/CMFCore/tests/fake_skins/fake_skin')
        self.assertEqual(self.ob.fake_skin.objectIds(),[])
        
class DirectoryViewTests( FSDVTest ):

    def setUp( self ):
        FSDVTest.setUp(self)
        self._registerDirectory(self)        

    def test_addDirectoryViews( self ):
        """ Test addDirectoryViews  """
        # also test registration of driectory views doesn't barf
        pass

    def test_DirectoryViewExists( self ):
        """
        Check DirectoryView added by addDirectoryViews
        appears as a DirectoryViewSurrogate due
        to Acquisition hackery.
        """
        from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
        self.failUnless(isinstance(self.ob.fake_skin,DirectoryViewSurrogate))

    def test_DirectoryViewMethod( self ):
        """ Check if DirectoryView method works """
        self.assertEqual(self.ob.fake_skin.test1(),'test1')

    def test_properties(self):
        """Make sure the directory view is reading properties"""
        self.assertEqual(self.ob.fake_skin.testPT.title, 'Zope Pope')

if DevelopmentMode:

  class DebugModeTests( FSDVTest ):

    def setUp( self ):
        FSDVTest.setUp(self)
        self.test1path = join(self.skin_path_name,'test1.py')
        self.test2path = join(self.skin_path_name,'test2.py')
        self.test3path = join(self.skin_path_name,'test3')
        
        # initialise skins
        self._registerDirectory(self)

        # add a method to the fake skin folder
        self._writeFile(self.test2path, "return 'test2'")

        # edit the test1 method
        self._writeFile(self.test1path, "return 'new test1'")

        # add a new folder
        mkdir(self.test3path)
        
    def test_AddNewMethod( self ):
        """
        See if a method added to the skin folder can be found
        """
        self.assertEqual(self.ob.fake_skin.test2(),'test2')

    def test_EditMethod( self ):
        """
        See if an edited method exhibits its new behaviour
        """
        self.assertEqual(self.ob.fake_skin.test1(),'new test1')

    def test_NewFolder( self ):
        """
        See if a new folder shows up
        """
        from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
        self.failUnless(isinstance(self.ob.fake_skin.test3,DirectoryViewSurrogate))
        self.ob.fake_skin.test3.objectIds()

    def test_DeleteMethod( self ):
        """
        Make sure a deleted method goes away
        """
        remove(self.test2path)
        self.failIf(hasattr(self.ob.fake_skin,'test2'))

    def test_DeleteAddEditMethod( self ):
        """
        Check that if we delete a method, then add it back,
        then edit it, the DirectoryView notices.

        This excecises yet another Win32 mtime weirdity.
        """
        remove(self.test2path)
        self.failIf(hasattr(self.ob.fake_skin,'test2'))
            
        # add method back to the fake skin folder
        self._writeFile(self.test2path, "return 'test2.2'")
        
        # check
        self.assertEqual(self.ob.fake_skin.test2(),'test2.2')

        
        # edit method
        self._writeFile(self.test2path, "return 'test2.3'")

        # check
        self.assertEqual(self.ob.fake_skin.test2(),'test2.3')
        
    def test_DeleteFolder( self ):
        """
        Make sure a deleted folder goes away
        """
        rmdir(self.test3path)
        self.failIf(hasattr(self.ob.fake_skin,'test3'))

else:

    class DebugModeTests( TestCase ):
        pass

def test_suite():
    return TestSuite((
        makeSuite(DirectoryViewPathTests),
        makeSuite(DirectoryViewTests),
        makeSuite(DebugModeTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')




