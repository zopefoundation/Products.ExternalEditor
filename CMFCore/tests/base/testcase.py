import Zope
from unittest import TestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Testing.makerequest import makerequest
from security import PermissiveSecurityPolicy, AnonymousUser
from dummy import DummyFolder
from os.path import join, abspath, dirname
from os import curdir, mkdir, stat, remove
from shutil import copytree,rmtree
from tempfile import mktemp

class TransactionalTest( TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root =  self.connection.root()[ 'Application' ]
    
    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()

class RequestTest( TransactionalTest ):
    
    def setUp(self):
        TransactionalTest.setUp(self)
        root = self.root = makerequest(self.root)
        self.REQUEST  = root.REQUEST
        self.RESPONSE = root.REQUEST.RESPONSE

class SecurityTest( TestCase ):

    def setUp(self):
        get_transaction().begin()
        self._policy = PermissiveSecurityPolicy()
        self._oldPolicy = setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        self.root =  self.connection.root()[ 'Application' ]
        newSecurityManager( None, AnonymousUser().__of__( self.root ) )

    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        setSecurityPolicy(self._oldPolicy)

class SecurityRequestTest( SecurityTest ):
    
    def setUp(self):
        SecurityTest.setUp(self)
        self.root = makerequest(self.root)

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

_prefix = abspath(join(_prefix,'..'))

class FSDVTest( TestCase ):
    # Base class for FSDV test, creates a fake skin
    # copy that can be edited.

    _sourceprefix = _prefix
    _skinname = 'fake_skins'
    _layername = 'fake_skin'

    def _registerDirectory(self,object=None):
        from Products.CMFCore.DirectoryView import registerDirectory
        from Products.CMFCore.DirectoryView import addDirectoryViews
        registerDirectory(self._skinname, self.tempname)
        if object is not None:
            ob = self.ob = DummyFolder()
            addDirectoryViews(ob, self._skinname, self.tempname)
    
    def _writeFile(self, filename, stuff):
        # write some stuff to a file on disk
        # make sure the file's modification time has changed
        # also make sure the skin folder mod time ahs changed
        thePath = join(self.skin_path_name,filename)
        try:
            mtime1 = stat(thePath)[8]
        except:
            mtime1 = 0
        mtime2 = mtime1
        while mtime2==mtime1:
            f = open(thePath,'w')
            f.write(stuff)
            f.close()
            mtime2 = stat(thePath)[8]

    def _deleteFile(self,filename):
        remove(join(self.skin_path_name,filename))
        
    def setUp(self):
        # store the place where the skin copy will be created
        self.tempname = mktemp()
        # create the temporary folder
        mkdir(self.tempname)
        # copy the source fake skin to the new location
        copytree(join(self._sourceprefix,
                      self._skinname),
                 join(self.tempname,
                      self._skinname))
        # store the skin path name
        self.skin_path_name = join(self.tempname,self._skinname,self._layername)

    def tearDown(self):
        # kill the copy
        rmtree(self.tempname)

