""" Base classes for testing interface conformance.

Derived testcase classes should define '_getTargetClass()', which must
return the class being tested for conformance.

$Id$
"""

class ConformsToISetupContext:

    def test_ISetupContext_conformance( self ):

        from Products.CMFSetup.interfaces import ISetupContext
        from Interface.Verify import verifyClass

        verifyClass( ISetupContext, self._getTargetClass() )

class ConformsToIImportContext:

    def test_IImportContext_conformance( self ):

        from Products.CMFSetup.interfaces import IImportContext
        from Interface.Verify import verifyClass

        verifyClass( IImportContext, self._getTargetClass() )

class ConformsToIExportContext:

    def test_IExportContext_conformance( self ):

        from Products.CMFSetup.interfaces import IExportContext
        from Interface.Verify import verifyClass

        verifyClass( IExportContext, self._getTargetClass() )
