import Zope
from unittest import TestSuite, main
from sys import modules
def test_suite():
    suite = TestSuite()
    for name in [
        'test_ContentTypeRegistry',
        'test_PortalFolder',
        'test_TypesTool',
        'test_ActionsTool',
        'test_ActionInformation',
        'test_ActionProviderBase',
        'test_Expression',
        'test_CatalogTool',
        'test_DirectoryView',
        'test_FSPythonScript',
        'test_FSPageTemplate'
        ]:
        __import__('Products.CMFCore.tests.'+name,globals(),locals())
        suite.addTest(
            modules['Products.CMFCore.tests.'+name].test_suite()
            )
    return suite

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()
