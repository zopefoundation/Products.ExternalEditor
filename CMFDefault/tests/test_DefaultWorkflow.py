from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFDefault.DefaultWorkflow import DefaultWorkflowDefinition


class DefaultWorkflowDefinitionTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_workflow \
                import WorkflowDefinition as IWorkflowDefinition

        verifyClass(IWorkflowDefinition, DefaultWorkflowDefinition)


def test_suite():
    return TestSuite((
        makeSuite( DefaultWorkflowDefinitionTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
