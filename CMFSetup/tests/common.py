""" CMFSetup product:  unit test utilities.
"""

from Products.CMFCore.tests.base.testcase import SecurityRequestTest


class BaseRegistryTests( SecurityRequestTest ):

    def _makeOne( self, *args, **kw ):

        # Derived classes must implement _getTargetClass
        return self._getTargetClass()( *args, **kw )

    def _compareDOM( self, found_text, expected_text ):

        from xml.dom.minidom import parseString
        found = parseString( found_text )
        expected = parseString( expected_text )
        self.assertEqual( found.toxml(), expected.toxml() )
