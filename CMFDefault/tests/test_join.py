##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for adding members.

$Id$
"""

from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.tests.base.testcase import TransactionalTest


class MembershipTests( TransactionalTest ):

    def test_join( self ):
        factory = self.root.manage_addProduct['CMFSetup'].addConfiguredSite
        factory('site', 'CMFDefault:default', snapshot=False)
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

    def test_join_without_email( self ):
        factory = self.root.manage_addProduct['CMFSetup'].addConfiguredSite
        factory('site', 'CMFDefault:default', snapshot=False)
        site = self.root.site
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          'test_user',
                          'zzyyzz',
                          properties={'username':'test_user', 'email': ''}
                          )

    def test_join_with_variable_id_policies( self ):
        factory = self.root.manage_addProduct['CMFSetup'].addConfiguredSite
        factory('site', 'CMFDefault:default', snapshot=False)
        site = self.root.site
        member_id = 'test.user'

        # Test with the default policy: Names with "." should fail
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          member_id,
                          'zzyyzz',
                          properties={ 'username':'Test User'
                                     , 'email': 'foo@bar.com'
                                     }
                          )

        # Now change the policy to allow "."
        #import pdb; pdb.set_trace()
        new_pattern = "^[A-Za-z][A-Za-z0-9_\.]*$"
        site.portal_registration.manage_editIDPattern(new_pattern)
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': 'TestUser2'
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)


def test_suite():
    return TestSuite((
        makeSuite(MembershipTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
