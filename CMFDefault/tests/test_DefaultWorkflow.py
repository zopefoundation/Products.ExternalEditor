from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

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
