import Zope
from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():

    return build_test_suite('Products.CMFDefault.tests',[
        'test_Discussions',
        'test_Document',
        'test_NewsItem',
        'test_Link',
        'test_Favorite',
        'test_Image',
        'test_MetadataTool',
        'test_utils',
        'test_join',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
