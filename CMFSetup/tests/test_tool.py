##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Unit tests for CMFSetup tool.

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

import os
from StringIO import StringIO

from Acquisition import aq_base
from OFS.Folder import Folder

from common import DOMComparator
from common import DummyExportContext
from common import DummyImportContext
from common import FilesystemTestBase
from common import SecurityRequestTest
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

        toolset_registry = tool.getToolsetRegistry()
        self.assertEqual( len( toolset_registry.listForbiddenTools() ), 0 )
        self.assertEqual( len( toolset_registry.listRequiredTools() ), 0 )

    def test_getProfileDirectory_relative_no_product( self ):

        from Products.CMFSetup.tool import IMPORT_STEPS_XML
        from Products.CMFSetup.tool import EXPORT_STEPS_XML
        from Products.CMFSetup.tool import TOOLSET_XML
        from test_registry import _EMPTY_IMPORT_XML
        from test_registry import _EMPTY_EXPORT_XML
        from test_registry import _EMPTY_TOOLSET_XML
        from common import _makeTestFile

        tool = self._makeOne()

        _makeTestFile( IMPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _EMPTY_IMPORT_XML
                     )

        _makeTestFile( EXPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _EMPTY_EXPORT_XML
                     )

        _makeTestFile( TOOLSET_XML
                     , self._PROFILE_PATH
                     , _EMPTY_TOOLSET_XML
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

        from Products.CMFSetup.tool import IMPORT_STEPS_XML
        from Products.CMFSetup.tool import EXPORT_STEPS_XML
        from Products.CMFSetup.tool import TOOLSET_XML
        from test_registry import _SINGLE_IMPORT_XML
        from test_registry import _SINGLE_EXPORT_XML
        from test_registry import _NORMAL_TOOLSET_XML
        from test_registry import ONE_FUNC
        from common import _makeTestFile

        tool = self._makeOne()

        _makeTestFile( IMPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _SINGLE_IMPORT_XML
                     )

        _makeTestFile( EXPORT_STEPS_XML
                     , self._PROFILE_PATH
                     , _SINGLE_EXPORT_XML
                     )

        _makeTestFile( TOOLSET_XML
                     , self._PROFILE_PATH
                     , _NORMAL_TOOLSET_XML
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

        toolset = tool.getToolsetRegistry()
        self.assertEqual( len( toolset.listForbiddenTools() ), 1 )
        self.failUnless( 'doomed' in toolset.listForbiddenTools() )
        self.assertEqual( len( toolset.listRequiredTools() ), 2 )
        self.failUnless( 'mandatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'mandatory' )
        self.assertEqual( info[ 'class' ], 'path.to.one' )
        self.failUnless( 'obligatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'obligatory' )
        self.assertEqual( info[ 'class' ], 'path.to.another' )

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

        toolset = tool.getToolsetRegistry()
        self.assertEqual( len( toolset.listForbiddenTools() ), 1 )
        self.failUnless( 'doomed' in toolset.listForbiddenTools() )
        self.assertEqual( len( toolset.listRequiredTools() ), 2 )
        self.failUnless( 'mandatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'mandatory' )
        self.assertEqual( info[ 'class' ], 'path.to.one' )
        self.failUnless( 'obligatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'obligatory' )
        self.assertEqual( info[ 'class' ], 'path.to.another' )

    def test_setProfileDirectory_relative_encode_as_ascii( self ):

        import Products.CMFSetup
        from common import dummy_handler

        _PATH = 'tests/default_profile'
        _PRODUCT_PATH = os.path.split( Products.CMFSetup.__file__ )[0]
        _FQPATH = os.path.join( _PRODUCT_PATH, _PATH )

        tool = self._makeOne()
        tool.setProfileDirectory( _PATH, 'CMFSetup', encoding='ascii' )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        self.assertEqual( import_registry.getStep( 'one' ), dummy_handler )

        export_registry = tool.getExportStepRegistry()
        self.assertEqual( len( export_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        self.assertEqual( export_registry.getStep( 'one' ), dummy_handler )

        toolset = tool.getToolsetRegistry()
        self.assertEqual( len( toolset.listForbiddenTools() ), 1 )
        self.failUnless( 'doomed' in toolset.listForbiddenTools() )
        self.assertEqual( len( toolset.listRequiredTools() ), 2 )
        self.failUnless( 'mandatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'mandatory' )
        self.assertEqual( info[ 'class' ], 'path.to.one' )
        self.failUnless( 'obligatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'obligatory' )
        self.assertEqual( info[ 'class' ], 'path.to.another' )

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

class _ToolsetSetup( SecurityRequestTest ):

    def _initSite( self ):

        from Products.CMFSetup.tool import SetupTool
        site = Folder()
        site._setId( 'site' )
        self.root._setObject( 'site', site )
        site = self.root._getOb( 'site' )
        site._setObject( 'portal_setup', SetupTool() )
        return site

class Test_exportToolset( _ToolsetSetup
                        , DOMComparator
                        ):

    def test_empty( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import exportToolset

        site = self._initSite()
        context = DummyExportContext( site )

        exportToolset( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, TOOLSET_XML )
        self._compareDOM( text, _EMPTY_TOOLSET_XML )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import exportToolset

        site = self._initSite()
        toolset = site.portal_setup.getToolsetRegistry()
        toolset.addForbiddenTool( 'doomed' )
        toolset.addRequiredTool( 'mandatory', 'path.to.one' )
        toolset.addRequiredTool( 'obligatory', 'path.to.another' )

        context = DummyExportContext( site )

        exportToolset( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, TOOLSET_XML )
        self._compareDOM( text, _NORMAL_TOOLSET_XML )
        self.assertEqual( content_type, 'text/xml' )

class Test_importToolset( _ToolsetSetup ):

    def test_forbidden_tools( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import importToolset
        TOOL_IDS = ( 'doomed', 'blasted', 'saved' )

        site = self._initSite()

        for tool_id in TOOL_IDS:
            pseudo = Folder()
            pseudo._setId( tool_id )
            site._setObject( tool_id, pseudo )

        self.assertEqual( len( site.objectIds() ), len( TOOL_IDS ) + 1 )

        for tool_id in TOOL_IDS:
            self.failUnless( tool_id in site.objectIds() )

        context = DummyImportContext( site )
        context._files[ TOOLSET_XML ] = _FORBIDDEN_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 2 )
        self.failUnless( 'portal_setup' in site.objectIds() )
        self.failUnless( 'saved' in site.objectIds() )

    def test_required_tools_missing( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import importToolset

        site = self._initSite()
        self.assertEqual( len( site.objectIds() ), 1 )

        context = DummyImportContext( site )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )
        self.failUnless( isinstance( aq_base( site._getOb( 'mandatory' ) )
                                   , DummyTool ) )
        self.failUnless( isinstance( aq_base( site._getOb( 'obligatory' ) )
                                   , DummyTool ) )

    def test_required_tools_no_replacement( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import importToolset

        site = self._initSite()

        mandatory = DummyTool()
        mandatory._setId( 'mandatory' )
        site._setObject( 'mandatory', mandatory )

        obligatory = DummyTool()
        obligatory._setId( 'obligatory' )
        site._setObject( 'obligatory', obligatory )

        self.assertEqual( len( site.objectIds() ), 3 )

        context = DummyImportContext( site )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )
        self.failUnless( aq_base( site._getOb( 'mandatory' ) ) is mandatory )
        self.failUnless( aq_base( site._getOb( 'obligatory' ) ) is obligatory )

    def test_required_tools_with_replacement( self ):

        from Products.CMFSetup.tool import TOOLSET_XML
        from Products.CMFSetup.tool import importToolset

        site = self._initSite()

        mandatory = AnotherDummyTool()
        mandatory._setId( 'mandatory' )
        site._setObject( 'mandatory', mandatory )

        obligatory = AnotherDummyTool()
        obligatory._setId( 'obligatory' )
        site._setObject( 'obligatory', obligatory )

        self.assertEqual( len( site.objectIds() ), 3 )

        context = DummyImportContext( site )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )

        self.failIf( aq_base( site._getOb( 'mandatory' ) ) is mandatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'mandatory' ) )
                                   , DummyTool ) )

        self.failIf( aq_base( site._getOb( 'obligatory' ) ) is obligatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'obligatory' ) )
                                   , DummyTool ) )


class DummyTool( Folder ):

    pass

class AnotherDummyTool( Folder ):

    pass

_EMPTY_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
</tool-setup>
"""

_NORMAL_TOOLSET_XML = """\
<?xml version="1.0" ?>
<tool-setup>
<forbidden tool_id="doomed"/>
<required class="path.to.one" tool_id="mandatory"/>
<required class="path.to.another" tool_id="obligatory"/>
</tool-setup>
"""

_FORBIDDEN_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="doomed" />
 <forbidden tool_id="damned" />
 <forbidden tool_id="blasted" />
</tool-setup>
"""

_REQUIRED_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <required
    tool_id="mandatory"
    class="Products.CMFSetup.tests.test_tool.DummyTool" />
 <required
    tool_id="obligatory"
    class="Products.CMFSetup.tests.test_tool.DummyTool" />
</tool-setup>
"""

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SetupToolTests ),
        unittest.makeSuite( Test_exportToolset ),
        unittest.makeSuite( Test_importToolset ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
