""" Unit tests for CMFSetup tool.

$Id$
"""

import unittest
import os
from StringIO import StringIO

from common import FilesystemTestBase
from common import TarballTester
from conformance import ConformsToISetupTool

class SetupToolTests( FilesystemTestBase
                    , TarballTester
                    , ConformsToISetupTool
                    ):

    _PROFILE_PATH = '/tmp/STT_test'

    def _getTargetClass( self ):

        from Products.CMFSetup.tool import SetupTool
        return SetupTool

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def _makeSite( self, title="Don't care" ):

        from OFS.Folder import Folder

        site = Folder()
        site._setId( 'site' )
        site.title = title

        self.root._setObject( 'site', site )
        return self.root._getOb( 'site' )

    def test_empty( self ):

        tool = self._makeOne()

        self.assertEqual( tool.getProfileProduct(), None )
        self.assertEqual( tool.getProfileDirectory(), None )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 0 )

        export_registry = tool.getExportStepRegistry()
        export_steps = export_registry.listSteps() 
        self.assertEqual( len( export_steps ), 1 )
        self.assertEqual( export_steps[ 0 ], 'step_registries' )

    def test_getProfileDirectory_relative_no_product( self ):

        from test_registry import _EMPTY_IMPORT_XML
        from test_registry import _EMPTY_EXPORT_XML
        from common import _makeTestFile

        tool = self._makeOne()

        _makeTestFile( tool.IMPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _EMPTY_IMPORT_XML
                     )

        _makeTestFile( tool.EXPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _EMPTY_EXPORT_XML
                     )

        tool.setProfileDirectory( self._PROFILE_PATH )

        self.assertEqual( tool.getProfileDirectory( True ), self._PROFILE_PATH )

    def test_setProfileDirectory_absolute_invalid( self ):

        tool = self._makeOne()

        self.assertRaises( ValueError
                         , tool.setProfileDirectory
                         , self._PROFILE_PATH
                         )

    def test_setProfileDirectory_absolute( self ):

        from test_registry import _SINGLE_IMPORT_XML
        from test_registry import _SINGLE_EXPORT_XML
        from test_registry import ONE_FUNC
        from common import _makeTestFile

        tool = self._makeOne()

        _makeTestFile( tool.IMPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _SINGLE_IMPORT_XML
                     )

        _makeTestFile( tool.EXPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _SINGLE_EXPORT_XML
                     )

        tool.setProfileDirectory( self._PROFILE_PATH )

        self.assertEqual( tool.getProfileProduct(), None )
        self.assertEqual( tool.getProfileDirectory(), self._PROFILE_PATH )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = import_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.assertEqual( info[ 'version' ], '1' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.CMFSetup.tests.test_registry.ONE_FUNC' )

        self.assertEqual( import_registry.getStep( 'one' ), ONE_FUNC )

        export_registry = tool.getExportStepRegistry()
        self.assertEqual( len( export_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = export_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.CMFSetup.tests.test_registry.ONE_FUNC' )

        self.assertEqual( export_registry.getStep( 'one' ), ONE_FUNC )

    def test_setProfileDirectory_relative_invalid( self ):

        _PATH = 'tests/nonesuch'

        tool = self._makeOne()

        self.assertRaises( ValueError
                         , tool.setProfileDirectory
                         , _PATH
                         , 'CMFSetup'
                         )

    def test_setProfileDirectory_relative( self ):

        import Products.CMFSetup
        from common import dummy_handler

        _PATH = 'tests/default_profile'
        _PRODUCT_PATH = os.path.split( Products.CMFSetup.__file__ )[0]
        _FQPATH = os.path.join( _PRODUCT_PATH, _PATH )

        tool = self._makeOne()
        tool.setProfileDirectory( _PATH, 'CMFSetup' )

        self.assertEqual( tool.getProfileProduct(), 'CMFSetup' )
        self.assertEqual( tool.getProfileDirectory(), _FQPATH )
        self.assertEqual( tool.getProfileDirectory( True ), _PATH )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = import_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.assertEqual( info[ 'version' ], '1' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.CMFSetup.tests.common.dummy_handler' )
        self.assertEqual( import_registry.getStep( 'one' ), dummy_handler )

        export_registry = tool.getExportStepRegistry()
        self.assertEqual( len( export_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = export_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.CMFSetup.tests.common.dummy_handler' )
        self.assertEqual( export_registry.getStep( 'one' ), dummy_handler )

    def test_setProfileDirectory_relative_invalid_product( self ):

        _PATH = 'tests/default_profile'
        tool = self._makeOne()

        self.assertRaises( ValueError           
                         , tool.setProfileDirectory, _PATH, 'NonesuchProduct' )

    def test_runImportStep_nonesuch( self ):

        site = self._makeSite()

        tool = self._makeOne().__of__( site )

        self.assertRaises( ValueError, tool.runImportStep, 'nonesuch' )

    def test_runImportStep_simple( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'simple', '1', _uppercaseSiteTitle )

        result = tool.runImportStep( 'simple' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'simple' )
        self.assertEqual( result[ 'messages' ][ 'simple' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.upper() )

    def test_runImportStep_dependencies( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1', _underscoreSiteTitle )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )

        result = tool.runImportStep( 'dependent' )

        self.assertEqual( len( result[ 'steps' ] ), 2 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'dependable' )
        self.assertEqual( result[ 'messages' ][ 'dependable' ]
                        , 'Underscored title' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )
        self.assertEqual( site.title, TITLE.replace( ' ', '_' ).upper() )

    def test_runImportStep_skip_dependencies( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1', _underscoreSiteTitle )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )

        result = tool.runImportStep( 'dependent', run_dependencies=False )

        self.assertEqual( len( result[ 'steps' ] ), 1 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.upper() )

    def test_runImportStep_default_purge( self ):

        site = self._makeSite()

        tool = self._makeOne().__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStep( 'purging' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Purged' )
        self.failUnless( site.purged )

    def test_runImportStep_explicit_purge( self ):

        site = self._makeSite()

        tool = self._makeOne().__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStep( 'purging', purge_old=True )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Purged' )
        self.failUnless( site.purged )

    def test_runImportStep_skip_purge( self ):

        site = self._makeSite()

        tool = self._makeOne().__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStep( 'purging', purge_old=False )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Unpurged' )
        self.failIf( site.purged )

    def test_runImportStep_consistent_context( self ):

        site = self._makeSite()

        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'purging', ) )

        result = tool.runImportStep( 'dependent', purge_old=False )
        self.failIf( site.purged )

    def test_runAllImportSteps_empty( self ):

        site = self._makeSite()
        tool = self._makeOne().__of__( site )

        result = tool.runAllImportSteps()
        
        self.assertEqual( len( result[ 'steps' ] ), 0 )

    def test_runAllImportSteps_sorted_default_purge( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )
        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportSteps()
        
        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Purged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'messages' ][ 'dependable' ]
                        , 'Underscored title' )

        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.replace( ' ', '_' ).upper() )
        self.failUnless( site.purged )

    def test_runAllImportSteps_sorted_explicit_purge( self ):

        site = self._makeSite()
        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportSteps( purge_old=True )
        
        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Purged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.failUnless( site.purged )

    def test_runAllImportSteps_sorted_skip_purge( self ):

        site = self._makeSite()
        tool = self._makeOne().__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportSteps( purge_old=False )
        
        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Unpurged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.failIf( site.purged )

    def test_runExportStep_nonesuch( self ):

        site = self._makeSite()
        tool = self._makeOne().__of__( site )

        self.assertRaises( ValueError, tool.runExportStep, 'nonesuch' )

    def test_runExportStep_step_registry( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.portal_setup = self._makeOne()
        tool = site.portal_setup

        result = tool.runExportStep( 'step_registries' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , 'Step registries exported'
                        )
        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EMPTY_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

    def test_runAllExportSteps_default( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.portal_setup = self._makeOne()
        tool = site.portal_setup

        result = tool.runAllExportSteps()

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , 'Step registries exported'
                        )
        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EMPTY_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

    def test_runAllExportSteps_extras( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.portal_setup = self._makeOne()
        tool = site.portal_setup

        import_reg = tool.getImportStepRegistry()
        import_reg.registerStep( 'dependable', '1'
                               , _underscoreSiteTitle, ( 'purging', ) )
        import_reg.registerStep( 'dependent', '1'
                               , _uppercaseSiteTitle, ( 'dependable', ) )
        import_reg.registerStep( 'purging', '1'
                               , _purgeIfRequired )

        export_reg = tool.getExportStepRegistry()
        export_reg.registerStep( 'properties'
                               , _exportPropertiesINI )

        result = tool.runAllExportSteps()

        self.assertEqual( len( result[ 'steps' ] ), 2 )

        self.failUnless( 'properties' in result[ 'steps' ] )
        self.assertEqual( result[ 'messages' ][ 'properties' ]
                        , 'Exported properties'
                        )

        self.failUnless( 'step_registries' in result[ 'steps' ] )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , 'Step registries exported'
                        )

        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              , 'properties.ini'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EXTRAS_STEP_REGISTRIES_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _EXTRAS_STEP_REGISTRIES_EXPORT_XML )
        self._verifyTarballEntry( fileish, 'properties.ini'
                                , _PROPERTIES_INI % site.title  )

    def test_createSnapshot_default( self ):

        from test_registry import _EMPTY_IMPORT_XML

        _EXPECTED = [ ( 'import_steps.xml', _EMPTY_IMPORT_XML )
                    , ( 'export_steps.xml'
                      , _DEFAULT_STEP_REGISTRIES_EXPORT_XML
                      )
                    ]

        site = self._makeSite()
        site.portal_setup = self._makeOne()
        tool = site.portal_setup

        self.assertEqual( len( tool.listSnapshotInfo() ), 0 )

        result = tool.createSnapshot( 'default' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , 'Step registries exported'
                        )

        snapshot = result[ 'snapshot' ]

        self.assertEqual( len( snapshot.objectIds() ), len( _EXPECTED ) )

        for id in [ x[0] for x in _EXPECTED ]:
            self.failUnless( id in snapshot.objectIds() )

        fileobj = snapshot._getOb( 'import_steps.xml' )
        self.assertEqual( fileobj.read() , _EMPTY_IMPORT_XML )

        fileobj = snapshot._getOb( 'export_steps.xml' )
        self.assertEqual( fileobj.read() , _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

        self.assertEqual( len( tool.listSnapshotInfo() ), 1 )

        info = tool.listSnapshotInfo()[ 0 ]

        self.assertEqual( info[ 'id' ], 'default' )
        self.assertEqual( info[ 'title' ], 'default' )


_DEFAULT_STEP_REGISTRIES_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step id="step_registries"
              handler="Products.CMFSetup.tool.exportStepRegistries"
              title="Export import / export steps.">
  
 </export-step>
</export-steps>
"""

_EXTRAS_STEP_REGISTRIES_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step id="properties"
              handler="Products.CMFSetup.tests.test_tool._exportPropertiesINI"
              title="properties">
  
 </export-step>
 <export-step id="step_registries"
              handler="Products.CMFSetup.tool.exportStepRegistries"
              title="Export import / export steps.">
  
 </export-step>
</export-steps>
"""

_EXTRAS_STEP_REGISTRIES_IMPORT_XML = """\
<?xml version="1.0"?>
<import-steps>
 <import-step id="dependable"
              version="1"
              handler="Products.CMFSetup.tests.test_tool._underscoreSiteTitle"
              title="dependable">
  <dependency step="purging" />
  
 </import-step>
 <import-step id="dependent"
              version="1"
              handler="Products.CMFSetup.tests.test_tool._uppercaseSiteTitle"
              title="dependent">
  <dependency step="dependable" />
  
 </import-step>
 <import-step id="purging"
              version="1"
              handler="Products.CMFSetup.tests.test_tool._purgeIfRequired"
              title="purging">
  
 </import-step>
</import-steps>
"""

_PROPERTIES_INI = """\
[Default]
Title=%s
"""

def _underscoreSiteTitle( context ):

    site = context.getSite()
    site.title = site.title.replace( ' ', '_' )
    return 'Underscored title'

def _uppercaseSiteTitle( context ):

    site = context.getSite()
    site.title = site.title.upper()
    return 'Uppercased title'

def _purgeIfRequired( context ):

    site = context.getSite()
    purged = site.purged = context.shouldPurge()
    return purged and 'Purged' or 'Unpurged'

def _exportPropertiesINI( context ):

    site = context.getSite()
    text = _PROPERTIES_INI % site.title

    context.writeDataFile( 'properties.ini', text, 'text/plain' )

    return 'Exported properties'

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SetupToolTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
