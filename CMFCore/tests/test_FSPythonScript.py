from unittest import TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()

from os.path import join
from sys import exc_info
from thread import start_new_thread
from time import sleep

from OFS.Folder import Folder

from Products.CMFCore.FSPythonScript import FSPythonScript
from Products.CMFCore.tests.base.testcase import FSDVTest


class FSPythonScriptTests( FSDVTest ):

    def test_GetSize( self ):
        # Test get_size returns correct value
        script = FSPythonScript('test1', join(self.skin_path_name,'test1.py'))
        self.assertEqual(len(script.read()),script.get_size())

    def testInitializationRaceCondition(self):
        # Tries to exercise a former race condition where
        # FSObject._updateFromFS() set self._parsed before the
        # object was really parsed.
        for n in range(10):
            f = Folder()
            script = FSPythonScript('test1', join(self.skin_path_name,'test1.py')).__of__(f)
            res = []

            def call_script(script=script, res=res):
                try:
                    res.append(script())
                except:
                    res.append('%s: %s' % exc_info()[:2])

            start_new_thread(call_script, ())
            call_script()
            while len(res) < 2:
                sleep(0.05)
            self.assertEqual(res, ['test1', 'test1'], res)


def test_suite():
    return TestSuite((
        makeSuite(FSPythonScriptTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
