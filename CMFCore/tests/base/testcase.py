import Zope
from unittest import TestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Testing.makerequest import makerequest
from security import PermissiveSecurityPolicy, AnonymousUser

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
        root = self.root
        root = makerequest(root)
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
