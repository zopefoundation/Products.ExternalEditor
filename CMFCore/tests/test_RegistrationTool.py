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
""" Unit tests for RegistrationTool module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()


class RegistrationToolTests(TestCase):

    def _makeOne(self):
        from Products.CMFCore.RegistrationTool import RegistrationTool

        return RegistrationTool()

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.interfaces.portal_registration \
                import portal_registration as IRegistrationTool
        from Products.CMFCore.RegistrationTool import RegistrationTool

        verifyClass(IActionProvider, RegistrationTool)
        verifyClass(IRegistrationTool, RegistrationTool)

    def test_z3interfaces(self):
        try:
            from zope.interface.verify import verifyClass
        except ImportError:
            # BBB: for Zope 2.7
            return
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import IRegistrationTool
        from Products.CMFCore.RegistrationTool import RegistrationTool

        verifyClass(IActionProvider, RegistrationTool)
        verifyClass(IRegistrationTool, RegistrationTool)

    def test_generatePassword(self):
        rtool = self._makeOne()
        self.failUnless( len( rtool.generatePassword() ) >= 5 )


def test_suite():
    return TestSuite((
        makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
