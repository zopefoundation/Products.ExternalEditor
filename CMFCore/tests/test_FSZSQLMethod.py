from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
from Products.CMFCore.tests.base.testcase import FSDVTest


class FSZSQLMethodTests( FSDVTest ):

    def setUp(self):
        FSDVTest.setUp(self)
        self._registerDirectory(self)

    def test_initialization(self):
        zsql = self.ob.fake_skin.testsql
        self.assertEqual(zsql.title, 'This is a title')
        self.assertEqual(zsql.connection_id, 'testconn')
        self.assertEqual(zsql.arguments_src, 'id')
        self.assertEqual(zsql.max_rows_, 1000)
        self.assertEqual(zsql.max_cache_, 100)
        self.assertEqual(zsql.cache_time_, 10)
        self.assertEqual(zsql.class_name_, 'MyRecord')
        self.assertEqual(zsql.class_file_, 'CMFCore.TestRecord')
        self.assertEqual(zsql.connection_hook, 'MyHook')


def test_suite():
    return TestSuite((
        makeSuite(FSZSQLMethodTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
