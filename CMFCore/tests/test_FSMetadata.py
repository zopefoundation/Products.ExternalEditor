import Zope

from unittest import TestSuite, makeSuite, main
from types import ListType
from os import remove
from os.path import join
from time import sleep

from Products.CMFCore.tests.base.testcase import RequestTest
from Products.CMFCore.tests.base.testcase import FSDVTest

from Globals import DevelopmentMode

from test_FSSecurity import FSSecurityBase
        
class FSMetadata(FSSecurityBase):

    def _checkProxyRoles(self, obj, roles):
        """ Test proxy roles on the object """
        for role in roles:
            if not obj.manage_haveProxy(role):
                raise 'Object does not have the "%s" role' % role

    def test_basicPermissions(self):
        """ Test basic FS permissions """
        # check it has a title
        assert(self.ob.fake_skin.test6.title == 'Test object')
        self._checkSettings(
            self.ob.fake_skin.test6,
            'Access contents information',
            1,
            ['Manager','Anonymous'])
    
    def test_proxy(self):
        """ Test roles """
        ob = self.ob.fake_skin.test_dtml
        self._checkProxyRoles(ob, ['Manager', 'Anonymous'])

def test_suite():
    return TestSuite((
        makeSuite(FSMetadata),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')




