from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from os import remove, mkdir, rmdir
from os.path import join
from tempfile import mktemp

from Globals import DevelopmentMode

from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.testcase import _prefix
from Products.CMFCore.tests.base.testcase import FSDVTest

from Products.CMFCore.DirectoryView import DirectoryView


class DummyDirectoryView(DirectoryView):
    def __of__(self, parent):
        return DummyDirectoryViewSurrogate()

class DummyDirectoryViewSurrogate:
    pass


class DirectoryViewPathTests( TestCase ):
    """
    These test that, no matter what is stored in their dirpath,
    FSDV's will do their best to find an appropriate skin
    and only do nothing in the case where an appropriate skin
    can't be found.
    """

    def setUp(self):
        from Products.CMFCore.DirectoryView import registerDirectory
        from Products.CMFCore.DirectoryView import addDirectoryViews
        registerDirectory('fake_skins', _prefix)
        self.ob = DummyFolder()
        addDirectoryViews(self.ob, 'fake_skins', _prefix)

    def test_getDirectoryInfo(self):
        skin = self.ob.fake_skin
        skin.manage_properties('CMFCore/tests/fake_skins/fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # 1 - 7, in effect, test the pre CMF 1.5 backwards compatibility code in
    # DirectoryView's __of__ method. See DirectoryView.py for details

    # windows INSTANCE_HOME
    def test_getDirectoryInfo1(self):
        skin = self.ob.fake_skin
        skin.manage_properties(r'Products\CMFCore\tests\fake_skins\fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # windows SOFTWARE_HOME
    def test_getDirectoryInfo2(self):
        skin = self.ob.fake_skin
        skin.manage_properties(
                  r'C:\Zope\2.5.1\Products\CMFCore\tests\fake_skins\fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # *nix INSTANCE_HOME
    def test_getDirectoryInfo3(self):
        skin = self.ob.fake_skin
        skin.manage_properties('Products/CMFCore/tests/fake_skins/fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # *nix SOFTWARE_HOME
    def test_getDirectoryInfo4(self):
        skin = self.ob.fake_skin
        skin.manage_properties(
           '/usr/local/zope/2.5.1/Products/CMFCore/tests/fake_skins/fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # windows PRODUCTS_PATH
    def test_getDirectoryInfo5(self):
        skin = self.ob.fake_skin
        skin.manage_properties( mktemp() +
                               r'\Products\CMFCore\tests\fake_skins\fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # linux PRODUCTS_PATH
    def test_getDirectoryInfo6(self):
        skin = self.ob.fake_skin
        skin.manage_properties( mktemp() +
                                '/Products/CMFCore/tests/fake_skins/fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # second 'Products' in path
    def test_getDirectoryInfo7(self):
        skin = self.ob.fake_skin
        skin.manage_properties(
           r'C:\CoolProducts\Zope\Products\CMFCore\tests\fake_skins\fake_skin')
        self.failUnless( hasattr(self.ob.fake_skin, 'test1'),
                         self.ob.fake_skin.getDirPath() )

    # Test we do nothing if given a really wacky path
    def test_UnhandleableExpandPath( self ):
        from tempfile import mktemp
        self.ob.fake_skin.manage_properties(mktemp())
        self.assertEqual(self.ob.fake_skin.objectIds(),[])

    def test_UnhandleableMinimalPath( self ):
        from Products.CMFCore.utils import minimalpath, normalize
        from tempfile import mktemp
        weirdpath = mktemp()
        # we need to normalize 'cos minimalpath does, btu we're not testing
        # normalize in this unit test.
        self.assertEqual( normalize(weirdpath), minimalpath(weirdpath) )

    # this test tests that registerDirectory calls minimalpath correctly
    # the only way to test this works under SOFTWARE_HOME,INSTANCE_HOME and
    # PRODUCTS_PATH setups is to run the test in those environments
    def test_registerDirectoryMinimalPath(self):
        from Products.CMFCore.DirectoryView import _dirreg
        dirs = _dirreg._directories
        self.failUnless( dirs.has_key('CMFCore/tests/fake_skins/fake_skin'),
                         dirs.keys() )
        self.assertEqual( self.ob.fake_skin.getDirPath(),
                          'CMFCore/tests/fake_skins/fake_skin' )


class DirectoryViewTests( FSDVTest ):

    def setUp( self ):
        FSDVTest.setUp(self)
        self._registerDirectory(self)

    def test_addDirectoryViews( self ):
        # Test addDirectoryViews
        # also test registration of directory views doesn't barf
        pass

    def test_DirectoryViewExists( self ):
        # Check DirectoryView added by addDirectoryViews
        # appears as a DirectoryViewSurrogate due
        # to Acquisition hackery.
        from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
        self.failUnless(isinstance(self.ob.fake_skin,DirectoryViewSurrogate))

    def test_DirectoryViewMethod( self ):
        # Check if DirectoryView method works
        self.assertEqual(self.ob.fake_skin.test1(),'test1')

    def test_properties(self):
        # Make sure the directory view is reading properties
        self.assertEqual(self.ob.fake_skin.testPT.title, 'Zope Pope')

    def test_ignored(self):
        # Test that the .test1.py is ignored
        assert('#test1' not in self.ob.fake_skin.objectIds())


class DirectoryViewFolderTests(FSDVTest):

    def setUp(self):
        FSDVTest.setUp(self)
        self._registerDirectory(self)

    def tearDown(self):
        from Products.CMFCore import DirectoryView
        # This is nasty, but there is no way to unregister anything
        # right now...
        metatype_registry = DirectoryView._dirreg._meta_types
        if 'FOLDER' in metatype_registry.keys():
            del metatype_registry['FOLDER']
        FSDVTest.tearDown(self)

    def test_DirectoryViewFolderDefault(self):
        # Test that a folder inside the fake skin really is of type
        # DirectoryViewSurrogate
        from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
        testfolder = self.ob.fake_skin.test_directory
        self.failUnless(isinstance(testfolder, DirectoryViewSurrogate))

    def test_DirectoryViewFolderCustom(self):
        # Now we register a different class under the fake meta_type
        # "FOLDER" and test again...
        from Products.CMFCore.DirectoryView import registerMetaType
        registerMetaType('FOLDER', DummyDirectoryView)

        # In order to regenerate the FSDV data we need to remove and
        # register again, that way the newly registered meta_type is used
        self.ob._delObject('fake_skin')
        self._registerDirectory(self)
        testfolder = self.ob.fake_skin.test_directory
        self.failUnless(isinstance(testfolder, DummyDirectoryViewSurrogate))


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
        # See if a method added to the skin folder can be found
        self.assertEqual(self.ob.fake_skin.test2(),'test2')

    def test_EditMethod( self ):
        # See if an edited method exhibits its new behaviour
        self.assertEqual(self.ob.fake_skin.test1(),'new test1')

    def test_NewFolder( self ):
        # See if a new folder shows up
        from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
        self.failUnless(isinstance(self.ob.fake_skin.test3,DirectoryViewSurrogate))
        self.ob.fake_skin.test3.objectIds()

    def test_DeleteMethod( self ):
        # Make sure a deleted method goes away
        remove(self.test2path)
        self.failIf(hasattr(self.ob.fake_skin,'test2'))

    def test_DeleteAddEditMethod( self ):
        # Check that if we delete a method, then add it back,
        # then edit it, the DirectoryView notices.
        # This exercises yet another Win32 mtime weirdity.
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
        # Make sure a deleted folder goes away
        rmdir(self.test3path)
        self.failIf(hasattr(self.ob.fake_skin,'test3'))

else:

    class DebugModeTests( TestCase ):
        pass


def test_suite():
    return TestSuite((
        makeSuite(DirectoryViewPathTests),
        makeSuite(DirectoryViewTests),
        makeSuite(DirectoryViewFolderTests),
        makeSuite(DebugModeTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
