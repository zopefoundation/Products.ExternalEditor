import Zope
from unittest import TestSuite, makeSuite, main

from Products.CMFCore.tests.base.testcase import \
     TransactionalTest

class MembershipTests( TransactionalTest ):

    def test_join( self ):
        self.root.manage_addProduct[ 'CMFDefault' ].manage_addCMFSite( 'site' )
        site = self.root.site
        member_id = 'test_user'
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': member_id
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)
        self.assertRaises(AttributeError,
                          getattr, site.Members, member_id)
        # test that wrapUser correctly creates member area
        site.portal_membership.setMemberareaCreationFlag()
        site.portal_membership.wrapUser(u)
        memberfolder = getattr(site.Members, member_id)
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
