from unittest import main

import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    # for Zope versions before 2.6.1
    pass

from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():
    return build_test_suite('Products.CMFDefault.tests',[
        'test_DefaultWorkflow',
        'test_Discussions',
        'test_DiscussionTool',
        'test_Document',
        'test_DublinCore',
        'test_Favorite',
        'test_Image',
        'test_join',
        'test_Link',
        'test_MembershipTool',
        'test_MetadataTool',
        'test_NewsItem',
        'test_Portal',
        'test_PropertiesTool',
        'test_RegistrationTool',
        'test_utils',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
