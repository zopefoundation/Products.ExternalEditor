import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.DirectoryView import registerDirectory,addDirectoryViews,DirectoryViewSurrogate
from Globals import package_home
from Acquisition import Implicit
from os import remove
from os.path import join
from shutil import copy2

# the path of our fake skin
skin_path_name = join(package_home(globals()),'fake_skins','fake_skin')

class DirectoryViewTests1( TestCase ):

    def setUp( self ):
        get_transaction().begin()
    
    def tearDown( self ):
        get_transaction().abort()

    def test_registerDirectory( self ):
        """ Test registerDirectory  """
        registerDirectory('fake_skins', globals())

class Dummy(Implicit):
    """
    A Dummy object to use in place of the skins tool
    """

    def _setObject(self,id,object):
        """ Dummy _setObject method """
        setattr(self,id,object)

class DirectoryViewTests2( TestCase ):

    def setUp( self ):
        get_transaction().begin()
        registerDirectory('fake_skins', globals())
        ob = self.ob = Dummy()
        addDirectoryViews(ob, 'fake_skins', globals())

    def tearDown( self ):
        get_transaction().abort()

    def test_addDirectoryViews( self ):
        """ Test addDirectoryViews  """
        pass

    def test_DirectoryViewExists( self ):
        """
        Check DirectoryView added by addDirectoryViews
        appears as a DirectoryViewSurrogate due
        to Acquisition hackery.
        """
        assert isinstance(self.ob.fake_skin,DirectoryViewSurrogate)

    def test_DirectoryViewMethod( self ):
        """ Check if DirectoryView method works """
        assert self.ob.fake_skin.test1()=='test1'

import Globals
import Products.CMFCore.DirectoryView

test1path = join(skin_path_name,'test1.py')
test2path = join(skin_path_name,'test2.py')

class DebugModeTests( TestCase ):

    def setUp( self ):
        get_transaction().begin()
        
        # put us in debug mode, preserve the DirectoryRegistry
        Globals.DevelopmentMode=1
        _dirreg = Products.CMFCore.DirectoryView._dirreg
        reload(Products.CMFCore.DirectoryView)
        Products.CMFCore.DirectoryView._dirreg = _dirreg
        

        # initialise skins
        Products.CMFCore.DirectoryView.registerDirectory('fake_skins', globals())
        ob = self.ob = Dummy()
        Products.CMFCore.DirectoryView.addDirectoryViews(ob, 'fake_skins', globals())
        
        # add a method to the fake skin folder
        f = open(test2path,'w')
        f.write("return 'test2'")
        f.close()

        # edit the test1 method
        copy2(test1path,test1path+'.bak')
        f = open(test1path,'w')
        f.write("return 'new test1'")
        f.close()

    def tearDown( self ):
        
        # undo FS changes
        remove(test1path)
        copy2(test1path+'.bak',test1path)
        remove(test1path+'.bak')
        remove(test2path)
        
        # take us out of debug mode, preserve the DirectoryRegistry
        Globals.DevelopmentMode=None
        _dirreg = Products.CMFCore.DirectoryView._dirreg
        reload(Products.CMFCore.DirectoryView)
        Products.CMFCore.DirectoryView._dirreg = _dirreg

        get_transaction().abort()

    def test_AddNewMethod( self ):
        """
        See if a method added to the skin folder can be found
        """
        assert self.ob.fake_skin.test2()=='test2'

    def test_EditMethod( self ):
        """
        See if an edited method exhibits its new behaviour
        """
        assert self.ob.fake_skin.test1()=='new test1'


def test_suite():
    return TestSuite((
        makeSuite(DirectoryViewTests1),
        makeSuite(DirectoryViewTests2),
        makeSuite(DebugModeTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()




