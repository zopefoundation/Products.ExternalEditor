import unittest
from Products.CMFDefault.tests import test_Discussions
from Products.CMFDefault.tests import test_Document
from Products.CMFDefault.tests import test_NewsItem
from Products.CMFDefault.tests import test_Image
from Products.CMFDefault.tests import test_MetadataTool
from Products.CMFDefault.tests import test_utils
# test_join is broken, because it tries to use a shortcut.
#from Products.CMFDefault.tests import test_join  

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( test_Discussions.test_suite() )
    suite.addTest( test_Document.test_suite() )
    suite.addTest( test_NewsItem.test_suite() )
    suite.addTest( test_Image.test_suite() )
    suite.addTest( test_MetadataTool.test_suite() )
    suite.addTest( test_utils.test_suite() )
    #suite.addTest( test_join.test_suite() )
    return suite

def run():
    unittest.JUnitTextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
