import Zope
from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():

    return build_test_suite('Products.CMFCore.tests',[
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
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
