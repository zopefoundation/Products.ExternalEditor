from unittest import TestSuite, makeSuite, main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from AccessControl import getSecurityManager
from AccessControl.Owned import Owned
from AccessControl.Permission import Permission

from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.utils import _checkPermission


class DummyObject(Owned, DummyObject):
    pass


class CoreUtilsTests(SecurityTest):

    def setUp(self):
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.site._setObject( 'acl_users', DummyUserFolder() )
        self.site._setObject('content_dummy', DummyObject(id='content_dummy'))
        self.site._setObject('actions_dummy', DummyObject(id='actions_dummy'))

    def test__checkPermission(self):
        o = self.site.actions_dummy
        Permission('View',(),o).setRoles(('Anonymous',))
        Permission('WebDAV access',(),o).setRoles(('Authenticated',))
        Permission('Manage users',(),o).setRoles(('Manager',))
        eo = self.site.content_dummy
        eo._owner = (['acl_users'], 'user_foo')
        getSecurityManager().addContext(eo)
        self.failUnless( _checkPermission('View', o) )
        self.failIf( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )

        eo._proxy_roles = ('Authenticated',)
        self.failIf( _checkPermission('View', o) )
        self.failUnless( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )


def test_suite():
    return TestSuite((
        makeSuite(CoreUtilsTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
