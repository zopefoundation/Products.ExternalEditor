import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.FSPythonScript import FSPythonScript
from test_DirectoryView import skin_path_name
from os.path import join

script_path = join(skin_path_name,'test1.py')

class FSPythonScriptTests( TestCase ):

    def test_registerDirectory( self ):
        """ Test get_size returns correct value """
        script = FSPythonScript('test1', script_path)
        self.assertEqual(len(script.read()),script.get_size())

def test_suite():
    return TestSuite((
        makeSuite(FSPythonScriptTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()




