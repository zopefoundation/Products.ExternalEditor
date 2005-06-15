##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCore tests.

$Id$
"""

from unittest import main
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.tests.base.utils import build_test_suite


def suite():
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
        'test_utils',
        'test_WorkflowTool',
        'testCookieCrumbler',
        ])

def test_suite():
    # Just to silence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')
