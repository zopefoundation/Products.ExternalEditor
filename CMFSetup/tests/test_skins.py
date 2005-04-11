##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for CMFSetup skins configurator

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

import os

from OFS.Folder import Folder
from OFS.SimpleItem import Item

from Products.CMFCore import DirectoryView
from Products.CMFCore.utils import expandpath
from Products.CMFCore.utils import minimalpath

from common import BaseRegistryTests
from common import DOMComparator
from common import DummyExportContext
from common import DummyImportContext

_TESTS_PATH = os.path.split( __file__ )[ 0 ]


class DummySite(Folder):
    _skin_setup_called = False
    def clearCurrentSkin(self):
        pass
    def setupCurrentSkin(self, REQUEST):
        self._skin_setup_called = True

class DummySkinsTool( Folder ):

    default_skin = 'default_skin'
    request_varname = 'request_varname'
    allow_any = False
    cookie_persistence = False

    def __init__( self, selections={}, fsdvs=[] ):

        self._selections = selections

        for id, obj in fsdvs:
            self._setObject( id, obj )

    def _getSelections( self ):

        return self._selections

    def getSkinPaths( self ):

        result = list( self._selections.items() )
        result.sort()
        return result

    def addSkinSelection( self, skinname, skinpath, test=0, make_default=0 ):

        self._selections[ skinname ] = skinpath

class DummyFSDV( Item ):

    meta_type = DirectoryView.DirectoryView.meta_type

    def __init__( self, id ):

        self.id = id
        self._dirpath = minimalpath( os.path.join(_TESTS_PATH, id) )

class _SkinsSetup( BaseRegistryTests ):

    def setUp( self ):
        BaseRegistryTests.setUp( self )
        self._olddirreg = DirectoryView._dirreg
        self._dirreg = DirectoryView._dirreg = DirectoryView.DirectoryRegistry()

    def tearDown( self ):
        DirectoryView._dirreg = self._olddirreg
        BaseRegistryTests.tearDown( self )

    def _initSite( self, selections=None, fsdvs=None ):

        if selections is None:
            selections = {}

        if fsdvs is None:
            fsdvs = []

        self.root.site = DummySite()

        for id, fsdv in fsdvs:
            self._registerDirectoryView( expandpath(fsdv._dirpath) )

        self.root.site.portal_skins = DummySkinsTool( selections, fsdvs )

        return self.root.site

    def _registerDirectoryView( self, dirpath, subdirs=0 ):

        self._dirreg.registerDirectoryByPath( dirpath, subdirs )

class SkinsToolConfiguratorTests( _SkinsSetup ):

    def _getTargetClass( self ):

        from Products.CMFSetup.skins import SkinsToolConfigurator
        return SkinsToolConfigurator

    def test_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listSkinPaths() ), 0 )
        self.assertEqual( len( configurator.listFSDirectoryViews() ), 0 )

    def test_listSkinPaths( self ):

        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS )
        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listSkinPaths() ), 2 )
        info_list = configurator.listSkinPaths()

        self.assertEqual( info_list[ 0 ][ 'id' ], 'basic' )
        self.assertEqual( info_list[ 0 ][ 'path' ]
                        , _PATHS[ 'basic' ].split( ', ' ) )

        self.assertEqual( info_list[ 1 ][ 'id' ], 'fancy' )
        self.assertEqual( info_list[ 1 ][ 'path' ]
                        , _PATHS[ 'fancy' ].split( ', ' ) )

    def test_listFSDirectoryViews( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        site = self._initSite( fsdvs=_FSDVS )
        configurator = self._makeOne( site ).__of__( site )

        info_list = configurator.listFSDirectoryViews()
        self.assertEqual( len( info_list ), len( _IDS ) )

        ids = list( _IDS )
        ids.sort()

        for i in range( len( ids ) ):
            self.assertEqual( info_list[ i ][ 'id' ], ids[ i ] )
            self.assertEqual( info_list[ i ][ 'directory' ]
                            , 'CMFSetup/tests/%s' % ids[ i ]
                            )

    def test_generateXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateXML(), _EMPTY_EXPORT )

    def test_generateXML_normal( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        tool = site.portal_skins
        tool.default_skin = 'basic'
        tool.request_varname = 'skin_var'
        tool.allow_any = True
        tool.cookie_persistence = True

        configurator = self._makeOne( site ).__of__( site )

        self._compareDOM( configurator.generateXML(), _NORMAL_EXPORT )

    def test_parseXML_empty( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

        configurator = self._makeOne( site ).__of__( site )
        tool_info = configurator.parseXML( _EMPTY_EXPORT )

        self.assertEqual( tool_info[ 'default_skin' ], "default_skin" )
        self.assertEqual( tool_info[ 'request_varname' ], "request_varname" )
        self.failIf( tool_info[ 'allow_any' ] )
        self.failIf( tool_info[ 'cookie_persistence' ] )
        self.assertEqual( len( tool_info[ 'skin_dirs' ] ), 0 )
        self.assertEqual( len( tool_info[ 'skin_paths' ] ), 0 )

    def test_parseXML_normal( self ):

        site = self._initSite()
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'one' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'two' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'three' ) )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 0 )
        self.assertEqual( len( skins_tool.objectItems() ), 0 )

        configurator = self._makeOne( site ).__of__( site )
        tool_info = configurator.parseXML( _NORMAL_EXPORT )

        self.assertEqual( tool_info[ 'default_skin' ], "basic" )
        self.assertEqual( tool_info[ 'request_varname' ], "skin_var" )
        self.failUnless( tool_info[ 'allow_any' ] )
        self.failUnless( tool_info[ 'cookie_persistence' ] )
        self.assertEqual( len( tool_info[ 'skin_dirs' ] ), 3 )
        self.assertEqual( len( tool_info[ 'skin_paths' ] ), 2 )



_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<skins-tool default_skin="default_skin"
            request_varname="request_varname"
            allow_any="False"
            cookie_persistence="False">
</skins-tool>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<skins-tool default_skin="basic"
            request_varname="skin_var"
            allow_any="True"
            cookie_persistence="True">
 <skin-directory id="one" directory="CMFSetup/tests/one" />
 <skin-directory id="three" directory="CMFSetup/tests/three" />
 <skin-directory id="two" directory="CMFSetup/tests/two" />
 <skin-path id="basic">
  <layer name="one" />
 </skin-path>
 <skin-path id="fancy">
  <layer name="three" />
  <layer name="two" />
  <layer name="one" />
 </skin-path>
</skins-tool>
"""

_FRAGMENT_IMPORT = """\
<?xml version="1.0"?>
<skins-tool>
 <skin-directory id="three" directory="CMFSetup/tests/three" />
 <skin-path id="*">
  <layer name="three" insert-before="two"/>
 </skin-path>
</skins-tool>
"""

_FRAGMENT2_IMPORT = """\
<?xml version="1.0"?>
<skins-tool>
 <skin-directory id="four" directory="CMFSetup/tests/four" />
 <skin-path id="*">
  <layer name="four" insert-after="three"/>
 </skin-path>
</skins-tool>
"""

_FRAGMENT3_IMPORT = """\
<?xml version="1.0"?>
<skins-tool>
 <skin-directory id="three" directory="CMFSetup/tests/three" />
 <skin-directory id="four" directory="CMFSetup/tests/four" />
 <skin-path id="*">
  <layer name="three" insert-before="*"/>
  <layer name="four" insert-after="*"/>
 </skin-path>
</skins-tool>
"""

class Test_exportSkinsTool( _SkinsSetup ):

    def test_empty( self ):

        site = self._initSite()
        context = DummyExportContext( site )

        from Products.CMFSetup.skins import exportSkinsTool
        exportSkinsTool( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'skins.xml' )
        self._compareDOM( text, _EMPTY_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        tool = site.portal_skins
        tool.default_skin = 'basic'
        tool.request_varname = 'skin_var'
        tool.allow_any = True
        tool.cookie_persistence = True

        context = DummyExportContext( site )

        from Products.CMFSetup.skins import exportSkinsTool
        exportSkinsTool( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'skins.xml' )
        self._compareDOM( text, _NORMAL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

class Test_importSkinsTool( _SkinsSetup ):

    def test_empty_default_purge( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

        context = DummyImportContext( site )
        context._files[ 'skins.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 0 )
        self.assertEqual( len( skins_tool.objectItems() ), 0 )

    def test_empty_explicit_purge( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

        context = DummyImportContext( site, True )
        context._files[ 'skins.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 0 )
        self.assertEqual( len( skins_tool.objectItems() ), 0 )

    def test_empty_skip_purge( self ):

        _IDS = ( 'one', 'two', 'three' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one'
                 , 'fancy' : 'three, two, one'
                 }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

        context = DummyImportContext( site, False )
        context._files[ 'skins.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

    def test_normal( self ):

        site = self._initSite()
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'one' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'two' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'three' ) )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 0 )
        self.assertEqual( len( skins_tool.objectItems() ), 0 )

        context = DummyImportContext( site )
        context._files[ 'skins.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "basic" )
        self.assertEqual( skins_tool.request_varname, "skin_var" )
        self.failUnless( skins_tool.allow_any )
        self.failUnless( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

    def test_normal_encode_as_ascii( self ):

        site = self._initSite()
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'one' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'two' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'three' ) )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 0 )
        self.assertEqual( len( skins_tool.objectItems() ), 0 )

        context = DummyImportContext( site, encoding='ascii' )
        context._files[ 'skins.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "basic" )
        self.assertEqual( skins_tool.request_varname, "skin_var" )
        self.failUnless( skins_tool.allow_any )
        self.failUnless( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        self.assertEqual( len( skins_tool.getSkinPaths() ), 2 )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

    def test_fragment_skip_purge(self):

        _IDS = ( 'one', 'two' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one', 'fancy' : 'two,one' }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'three' ) )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        skin_paths = skins_tool.getSkinPaths()
        self.assertEqual( len( skin_paths ), 2 )
        self.assertEqual( skin_paths[ 0 ], ( 'basic', 'one' ) )
        self.assertEqual( skin_paths[ 1 ], ( 'fancy', 'two,one' ) )
        self.assertEqual( len( skins_tool.objectItems() ), 2 )

        context = DummyImportContext( site, False )
        context._files[ 'skins.xml' ] = _FRAGMENT_IMPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        skin_paths = skins_tool.getSkinPaths()
        self.assertEqual( len( skin_paths ), 2 )
        self.assertEqual( skin_paths[ 0 ], ( 'basic', 'one,three' ) )
        self.assertEqual( skin_paths[ 1 ], ( 'fancy', 'three,two,one' ) )
        self.assertEqual( len( skins_tool.objectItems() ), 3 )

        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'four' ) )
        context._files[ 'skins.xml' ] = _FRAGMENT2_IMPORT
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        skin_paths = skins_tool.getSkinPaths()
        self.assertEqual( len( skin_paths ), 2 )
        self.assertEqual( skin_paths[ 0 ], ( 'basic', 'one,three,four' ) )
        self.assertEqual( skin_paths[ 1 ], ( 'fancy', 'three,four,two,one' ) )
        self.assertEqual( len( skins_tool.objectItems() ), 4 )

    def test_fragment3_skip_purge(self):

        _IDS = ( 'one', 'two' )
        _FSDVS = [ ( id, DummyFSDV( id ) ) for id in _IDS ]
        _PATHS = { 'basic' : 'one', 'fancy' : 'two,one' }

        site = self._initSite( selections=_PATHS, fsdvs=_FSDVS )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'three' ) )
        self._registerDirectoryView( os.path.join( _TESTS_PATH, 'four' ) )
        skins_tool = site.portal_skins

        self.failIf( site._skin_setup_called )
        skin_paths = skins_tool.getSkinPaths()
        self.assertEqual( len( skin_paths ), 2 )
        self.assertEqual( skin_paths[ 0 ], ( 'basic', 'one' ) )
        self.assertEqual( skin_paths[ 1 ], ( 'fancy', 'two,one' ) )
        self.assertEqual( len( skins_tool.objectItems() ), 2 )

        context = DummyImportContext( site, False )
        context._files[ 'skins.xml' ] = _FRAGMENT3_IMPORT

        from Products.CMFSetup.skins import importSkinsTool
        importSkinsTool( context )

        self.assertEqual( skins_tool.default_skin, "default_skin" )
        self.assertEqual( skins_tool.request_varname, "request_varname" )
        self.failIf( skins_tool.allow_any )
        self.failIf( skins_tool.cookie_persistence )

        self.failUnless( site._skin_setup_called )
        skin_paths = skins_tool.getSkinPaths()
        self.assertEqual( len( skin_paths ), 2 )
        self.assertEqual( skin_paths[ 0 ], ( 'basic', 'three,one,four' ) )
        self.assertEqual( skin_paths[ 1 ],
                          ( 'fancy', 'three,two,one,four' ) )
        self.assertEqual( len( skins_tool.objectItems() ), 4 )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SkinsToolConfiguratorTests ),
        unittest.makeSuite( Test_exportSkinsTool ),
        unittest.makeSuite( Test_importSkinsTool ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
