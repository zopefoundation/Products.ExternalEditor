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
        self.failUnless( site.acl_users.getUser( 'test_user' ) )
        memberfolder = site.Members.test_user
        homepage = memberfolder.index_html
        self.assertEqual( memberfolder.Title(), "test_user's Home" )
        tool = site.portal_workflow
        self.assertEqual( tool.getInfoFor( homepage, 'review_state' )
                        , "private" )

    def test_join_without_email( self ):
        self.root.manage_addProduct[ 'CMFDefault' ].manage_addCMFSite( 'site' )
        site = self.root.site
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          'test_user',
                          'zzyyzz',
                          properties={'username':'test_user', 'email': ''}
                          )

def test_suite():
    return TestSuite((
        makeSuite(MembershipTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
