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
    return build_test_suite('Products.CMFCore.tests',[
        'test_ActionInformation',
        'test_ActionProviderBase',
        'test_ActionsTool',
        'test_CachingPolicyManager',
        'test_CatalogTool',
        'test_ContentTypeRegistry',
        'test_DirectoryView',
        'test_DiscussionTool',
        'test_DynamicType',
        'test_Expression',
        'test_FSFile',
        'test_FSImage',
        'test_FSMetadata',
        'test_FSPageTemplate',
        'test_FSPythonScript',
        'test_FSSecurity',
        'test_MemberDataTool',
        'test_MembershipTool',
        'test_OpaqueItems',
        'test_PortalContent',
        'test_PortalFolder',
        'test_RegistrationTool',
        'test_SkinsTool',
        'test_TypesTool',
        'test_UndoTool',
        'test_URLTool',
        'test_WorkflowTool',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
