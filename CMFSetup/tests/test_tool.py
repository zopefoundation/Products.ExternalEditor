""" Unit tests for CMFSetup tool.

$Id$
"""

import unittest

from Products.CMFCore.tests.base.testcase import SecurityRequestTest

from conformance import ConformsToISetupTool

class SetupToolTests( SecurityRequestTest
                    , ConformsToISetupTool
                    ):

    def _getTargetClass( self ):

        from Products.CMFSetup.tool import SetupTool
        return SetupTool

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def test_empty( self ):

        tool = self._makeOne()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SetupToolTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
