import Zope
import unittest

class MembershipTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self.root = Zope.app()

    def tearDown( self ):
        del self.root
        get_transaction().abort()

    def test_join( self ):
        self.root.manage_addProduct[ 'CMFDefault' ].manage_addCMFSite( 'site' )
        site = self.root.site
        site.portal_registration.addMember( 'test_user'
                                          , 'zzyyzz'
                                          , properties={ 'username':'test_user'
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        assert site.acl_users.getUser( 'test_user' )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( MembershipTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
