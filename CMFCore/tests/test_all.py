import unittest
from Products.CMFCore.tests import test_ContentTypeRegistry
from Products.CMFCore.tests import test_PortalFolder

def main():
    """\
    Combines all of the test suites in this package into a single
    large test.
    """
    suite = unittest.TestSuite((
        test_ContentTypeRegistry.test_suite(),
        test_PortalFolder.test_suite(),
        ))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()

