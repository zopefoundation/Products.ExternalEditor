import unittest
from Products.CMFCore.tests.base.testcase import RequestTest

import Testing
import Zope
Zope.startup()

class FauxMembershipTool:

    def getMemberById( self, username ):
        return None

class RegistrationToolTests(RequestTest):

    def _getTargetClass(self):

        from Products.CMFDefault.RegistrationTool import RegistrationTool
        return RegistrationTool

    def _makeOne(self, *args, **kw):

        return self._getTargetClass()(*args, **kw)

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_registration \
                import portal_registration as IRegistrationTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Interface.Verify import verifyClass

        verifyClass(IRegistrationTool, self._getTargetClass())
        verifyClass(IActionProvider, self._getTargetClass())

    def test_testPropertiesValidity_email_with_plus( self ):

        # CMF Collector #322

        tool = self._makeOne().__of__( self.root )
        self.root.portal_membership = FauxMembershipTool()

        props = { 'email' : 'user+site@example.com'
                , 'username' : 'username'
                }

        result = tool.testPropertiesValidity( props, None )

        self.failUnless( result is None )

    def test_testPropertiesValidity_email_with_underscore( self ):
        # Test for collector item 326: Email alias ending w/underscore
        tool = self._makeOne().__of__( self.root )
        self.root.portal_membership = FauxMembershipTool()

        props = { 'email' : 'username_@example.com'
                , 'username' : 'username'
                }

        result = tool.testPropertiesValidity( props, None )

        self.failUnless( result is None )

    def test_testPropertiesValidity_new_invalid_email( self ):

        tool = self._makeOne().__of__( self.root )
        self.root.portal_membership = FauxMembershipTool()

        props = { 'email' : 'this is not an e-mail address'
                , 'username' : 'username'
                }

        result = tool.testPropertiesValidity( props, None )

        self.failIf( result is None, 'Invalid e-mail passed inspection' )

    def test_spamcannon_collector_243( self ):

        INJECTED_HEADERS = """
To:someone@example.com
cc:another_victim@elsewhere.example.com
From:someone@example.com
Subject:Hosed by Spam Cannon!

Spam, spam, spam
"""

        tool = self._makeOne().__of__( self.root )
        self.root.portal_membership = FauxMembershipTool()

        props = { 'email' : INJECTED_HEADERS
                , 'username' : 'username'
                }

        result = tool.testPropertiesValidity( props, None )

        self.failIf( result is None, 'Invalid e-mail passed inspection' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
