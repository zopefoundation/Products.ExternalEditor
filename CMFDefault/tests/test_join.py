import Zope
from unittest import TestSuite, makeSuite, main

from Products.CMFCore.tests.base.testcase import \
     TransactionalTest

class MembershipTests( TransactionalTest ):

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
    return TestSuite((
        makeSuite(MembershipTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
