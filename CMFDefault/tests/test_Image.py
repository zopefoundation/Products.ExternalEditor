import unittest, os, cStringIO

from Products.CMFDefault.Image import Image
from Products.CMFDefault import tests

TESTS_HOME = tests.__path__[0]
TEST_JPG = os.path.join(TESTS_HOME, 'TestImage.jpg')


class TestImageElement(unittest.TestCase):

    def setUp( self ):
        get_transaction().begin()

    def tearDown( self ):
        get_transaction().abort()

    def test_EditWithEmptyFile(self):
        """ Test handling of empty file uploads """
        image = Image('testimage')

        testfile = open(TEST_JPG, 'rb')
        image.edit(file=testfile)
        testfile.seek(0,2)
        testfilesize = testfile.tell()
        testfile.close()

        assert image.get_size() == testfilesize

        emptyfile = cStringIO.StringIO()
        image.edit(file=emptyfile)

        assert image.get_size() > 0
        assert image.get_size() == testfilesize
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImageElement))
    return suite

def run():
    suite = test_suite()
    return unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    import sys
    result = run()
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
        
