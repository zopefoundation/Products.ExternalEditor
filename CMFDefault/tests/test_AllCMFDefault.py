import unittest
from Products.CMFDefault.tests import test_Document, test_utils

def main():
    """\
    Combines all of the test suites in this package into a single
    large test.
    """
    suite = unittest.TestSuite((
        test_Document.test_suite(),
        test_utils.test_suite(),
        ))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
