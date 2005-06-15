##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for DefaultWorkflow module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()


class DefaultWorkflowDefinitionTests(TestCase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_workflow \
                import WorkflowDefinition as IWorkflowDefinition
        from Products.CMFDefault.DefaultWorkflow \
                import DefaultWorkflowDefinition

        verifyClass(IWorkflowDefinition, DefaultWorkflowDefinition)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IWorkflowDefinition
        from Products.CMFDefault.DefaultWorkflow \
                import DefaultWorkflowDefinition

        verifyClass(IWorkflowDefinition, DefaultWorkflowDefinition)


def test_suite():
    return TestSuite((
        makeSuite( DefaultWorkflowDefinitionTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
