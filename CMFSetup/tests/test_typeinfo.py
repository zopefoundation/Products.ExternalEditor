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
""" Unit tests for type information export import

$Id$
"""

import unittest
import Testing
import Zope
Zope.startup()

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext


class DummyTypeInfo( SimpleItem ):

    def __init__( self, info ):

        self.__dict__.update( info )

class DummyTypesTool( Folder ):

    def __init__( self, type_infos ):

        self._type_infos = type_infos

        for id, obj in [ ( x[ 'id' ], DummyTypeInfo( x ) )
                            for x in type_infos ]:
            self._setObject( id, obj )

    def listContentTypes( self ):

        return [ x[ 'id' ] for x in self._type_infos ]

    def getTypeInfo( self, id ):

        info = [ x for x in self._type_infos if x[ 'id' ] == id ]

        if len( info ) == 0:
            raise KeyError, id

        info = info[ 0 ]

        if 'product' in info.keys():
            return FactoryTypeInformation( **info )
        else:
            return ScriptableTypeInformation( **info )

class _TypeInfoSetup( BaseRegistryTests ):

    def _initSite( self, type_infos=() ):

        self.root.site = Folder( id='site' )

        self.root.site.portal_types = DummyTypesTool( type_infos )

        return self.root.site

class TypeInfoConfiguratorTests( _TypeInfoSetup ):

    def _getTargetClass( self ):

        from Products.CMFSetup.typeinfo import TypeInfoConfigurator
        return TypeInfoConfigurator

    def test_getTypeInfo_nonesuch( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )

        self.assertRaises( ValueError, configurator.getTypeInfo, 'qux' )

    def test_getTypeInfo_FTI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        found = configurator.getTypeInfo( 'foo' )
        expected = _TI_LIST[ 0 ]

        for key in ( 'id'
                   , 'title'
                   , 'description'
                   , 'factory'
                   , 'product'
                   , 'factory'
                   , 'immediate_view'
                   , 'filter_content_types'
                   , 'allowed_content_types'
                   , 'allow_discussion'
                   , 'global_allow'
                   , 'aliases'
                   ):
            self.assertEqual( found[ key ], expected[ key ] )

        for lkey, rkey in ( ( 'meta_type', 'content_meta_type' )
                          , ( 'icon', 'content_icon' )
                          ):
            self.assertEqual( found[ lkey ], expected[ rkey ] )

        self.assertEqual( len( found[ 'actions' ] )
                        , len( expected[ 'actions' ] )
                        )

        for i in range( len( expected[ 'actions' ] ) ):

            a_expected = expected[ 'actions' ][ i ]
            a_found = found[ 'actions' ][ i ]

            for k in ( 'id'
                     , 'action'
                     , 'permissions'
                     ):
                self.assertEqual( a_expected[ k ], a_found[ k ] )

            for lk, rk in ( ( 'name', 'title' )
                          ,
                          ):
                self.assertEqual( a_expected[ lk ], a_found[ rk ] )

    def test_getTypeInfo_STI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        found = configurator.getTypeInfo( 'bar' )
        expected = _TI_LIST[ 1 ]

        for key in ( 'id'
                   , 'title'
                   , 'description'
                   , 'constructor_path'
                   , 'permission'
                   , 'immediate_view'
                   , 'filter_content_types'
                   , 'allowed_content_types'
                   , 'allow_discussion'
                   , 'global_allow'
                   , 'aliases'
                   ):
            self.assertEqual( found[ key ], expected[ key ] )

        for lkey, rkey in ( ( 'meta_type', 'content_meta_type' )
                          , ( 'icon', 'content_icon' )
                          ):
            self.assertEqual( found[ lkey ], expected[ rkey ] )

        self.assertEqual( len( found[ 'actions' ] )
                        , len( expected[ 'actions' ] )
                        )

        for i in range( len( expected[ 'actions' ] ) ):

            a_expected = expected[ 'actions' ][ i ]
            a_found = found[ 'actions' ][ i ]

            for k in ( 'id'
                     , 'action'
                     , 'permissions'
                     ):
                self.assertEqual( a_expected[ k ], a_found[ k ] )

            for lk, rk in ( ( 'name', 'title' )
                          ,
                          ):
                self.assertEqual( a_expected[ lk ], a_found[ rk ] )

    def test_listTypeInfo_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listTypeInfo() ), 0 )

    def test_listTypeInfo_filled ( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )

        self.assertEqual( len( configurator.listTypeInfo() ), len( _TI_LIST ) )

        info_list = configurator.listTypeInfo()
        self.assertEqual( len( info_list ), len( _TI_LIST ) )

        _marker = object()

        for i in range( len( _TI_LIST ) ):
            found = info_list[ i ]
            expected = _TI_LIST[ i ]
            self.assertEqual( found[ 'id' ], expected[ 'id' ] )
            self.failUnless( found.get( 'filename', _marker ) is _marker )

    def test_listTypeInfo_with_filename ( self ):

        site = self._initSite( _TI_LIST_WITH_FILENAME )
        configurator = self._makeOne( site ).__of__( site )

        info_list = configurator.listTypeInfo()
        self.assertEqual( len( info_list ), len( _TI_LIST_WITH_FILENAME ) )

        for i in range( len( _TI_LIST_WITH_FILENAME ) ):
            found = info_list[ i ]
            expected = _TI_LIST_WITH_FILENAME[ i ]
            self.assertEqual( found[ 'id' ], expected[ 'id' ] )
            self.assertEqual( found[ 'filename' ]
                            , 'types/%s.xml'
                                % expected[ 'id' ].replace( ' ', '_' )
                            )

    def test_generateToolXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateToolXML(), _EMPTY_TOOL_EXPORT )

    def test_generateToolXML_normal( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateToolXML(), _NORMAL_TOOL_EXPORT )

    def test_generateToolXML_explicit_filename( self ):

        site = self._initSite( _TI_LIST_WITH_FILENAME )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateToolXML(), _FILENAME_EXPORT )

    def test_generateTypeXML_FTI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateTypeXML( 'foo' )
                        , _FOO_EXPORT % 'foo' )

    def test_generateTypeXML_STI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateTypeXML( 'bar' )
                        , _BAR_EXPORT % 'bar' )

    def test_parseToolXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        id_file_list = configurator.parseToolXML( _EMPTY_TOOL_EXPORT )
        self.assertEqual( len( id_file_list ), 0 )

    def test_parseToolXML_normal( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        id_file_list = configurator.parseToolXML( _NORMAL_TOOL_EXPORT )
        self.assertEqual( len( id_file_list ), 2 )

        self.assertEqual( id_file_list[ 0 ][ 0 ], 'foo' )
        self.assertEqual( id_file_list[ 0 ][ 1 ], 'types/foo.xml' )
        self.assertEqual( id_file_list[ 1 ][ 0 ], 'bar' )
        self.assertEqual( id_file_list[ 1 ][ 1 ], 'types/bar.xml' )

    def test_parseToolXML_with_filename( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )

        id_file_list = configurator.parseToolXML( _FILENAME_EXPORT )
        self.assertEqual( len( id_file_list ), 2 )

        self.assertEqual( id_file_list[ 0 ][ 0 ], 'foo object' )
        self.assertEqual( id_file_list[ 0 ][ 1 ], 'types/foo_object.xml' )
        self.assertEqual( id_file_list[ 1 ][ 0 ], 'bar object' )
        self.assertEqual( id_file_list[ 1 ][ 1 ], 'types/bar_object.xml' )

    def test_parseTypeXML_FTI( self ):

        site = self._initSite()
        tool = site.portal_types
        configurator = self._makeOne( site ).__of__( site )
        self.assertEqual( len( tool.objectIds() ), 0 )

        info_list = configurator.parseTypeXML( _FOO_EXPORT % 'foo' )

        self.assertEqual( len( info_list ), 1 )

        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'foo' )
        self.assertEqual( info[ 'title' ], 'Foo' )
        self.assertEqual( len( info[ 'aliases' ] ), 2 )

    def test_parseTypeXML_STI( self ):

        site = self._initSite()
        tool = site.portal_types
        configurator = self._makeOne( site ).__of__( site )
        self.assertEqual( len( tool.objectIds() ), 0 )

        info_list = configurator.parseTypeXML( _BAR_EXPORT % 'bar' )
        self.assertEqual( len( info_list ), 1 )

        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'bar' )
        self.assertEqual( info[ 'title' ], 'Bar' )
        self.assertEqual( len( info[ 'aliases' ] ), 2 )

    def test_parseTypeXML_actions( self ):

        site = self._initSite()
        tool = site.portal_types
        configurator = self._makeOne( site ).__of__( site )

        type_info_list = configurator.parseTypeXML( _FOO_EXPORT % 'foo' )

        type_info = type_info_list[ 0 ]
        action_info_list = type_info[ 'actions' ]
        self.assertEqual( len( action_info_list ), 3 )

        action_info = action_info_list[ 0 ]
        self.assertEqual( action_info[ 'id' ], 'view' )
        self.assertEqual( action_info[ 'title' ], 'View' )
        self.assertEqual( action_info[ 'permissions' ], ( 'View', ) )


_TI_LIST = ( { 'id'                     : 'foo'
             , 'title'                  : 'Foo'
             , 'description'            : 'Foo things'
             , 'content_meta_type'      : 'Foo Thing'
             , 'content_icon'           : 'foo.png'
             , 'product'                : 'CMFSetup'
             , 'factory'                : 'addFoo'
             , 'immediate_view'         : 'foo_view'
             , 'filter_content_types'   : False
             , 'allowed_content_types'  : ()
             , 'allow_discussion'       : False
             , 'global_allow'           : False
             , 'aliases'                : { '(Default)' : 'foo_view'
                                          , 'view'      : 'foo_view'
                                          }
             , 'actions'        :
                ( { 'id'            : 'view'
                  , 'name'          : 'View'
                  , 'action': 'string:${object_url}/foo_view'
                  , 'permissions'   : (View,)
                  }
                , { 'id'            : 'edit'
                  , 'name'          : 'Edit'
                  , 'action': 'string:${object_url}/foo_edit_form'
                  , 'permissions'   : (ModifyPortalContent,)
                  }
                , { 'id'            : 'metadata'
                  , 'name'          : 'Metadata'
                  , 'action': 'string:${object_url}/metadata_edit_form'
                  , 'permissions'   : (ModifyPortalContent,)
                  }
                )
             }
           , { 'id'                     : 'bar'
             , 'title'                  : 'Bar'
             , 'description'            : 'Bar things'
             , 'content_meta_type'      : 'Bar Thing'
             , 'content_icon'           : 'bar.png'
             , 'constructor_path'       : 'make_bar'
             , 'permission'             : 'Add portal content'
             , 'immediate_view'         : 'bar_view'
             , 'filter_content_types'   : True
             , 'allowed_content_types'  : ( 'foo', )
             , 'allow_discussion'       : True
             , 'global_allow'           : True
             , 'aliases'                : { '(Default)' : 'bar_view'
                                          , 'view'      : 'bar_view'
                                          }
             , 'actions'        :
                ( { 'id'            : 'view'
                  , 'name'          : 'View'
                  , 'action': 'string:${object_url}/bar_view'
                  , 'permissions'   : (View,)
                  }
                , { 'id'            : 'edit'
                  , 'name'          : 'Edit'
                  , 'action': 'string:${object_url}/bar_edit_form'
                  , 'permissions'   : (ModifyPortalContent,)
                  }
                , { 'id'            : 'contents'
                  , 'name'          : 'Contents'
                  , 'action': 'string:${object_url}/folder_contents'
                  , 'permissions'   : (AccessContentsInformation,)
                  }
                , { 'id'            : 'metadata'
                  , 'name'          : 'Metadata'
                  , 'action': 'string:${object_url}/metadata_edit_form'
                  , 'permissions'   : (ModifyPortalContent,)
                  }
                )
             }
           )

_TI_LIST_WITH_FILENAME = []

for original in _TI_LIST:
    duplicate = original.copy()
    duplicate[ 'id' ] = '%s object' % original[ 'id' ]
    _TI_LIST_WITH_FILENAME.append( duplicate )

_EMPTY_TOOL_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
</types-tool>
"""

_NORMAL_TOOL_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type id="foo" />
 <type id="bar" />
</types-tool>
"""

_FILENAME_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type id="foo object" filename="types/foo_object.xml" />
 <type id="bar object" filename="types/bar_object.xml" />
</types-tool>
"""

_FOO_EXPORT = """\
<type-info
   id="%s"
   kind="Factory-based Type Information"
   title="Foo"
   meta_type="Foo Thing"
   icon="foo.png"
   product="CMFSetup"
   factory="addFoo"
   immediate_view="foo_view"
   filter_content_types="False"
   allow_discussion="False"
   global_allow="False" >
  <description>Foo things</description>
  <aliases>
   <alias from="(Default)" to="foo_view" />
   <alias from="view" to="foo_view" />
  </aliases>
  <action
     action_id="view"
     title="View"
     url_expr="string:${object_url}/foo_view"
     condition_expr=""
     category="object"
     visible="True">
   <permission>View</permission>
  </action>
  <action
     action_id="edit"
     title="Edit"
     url_expr="string:${object_url}/foo_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
  <action
     action_id="metadata"
     title="Metadata"
     url_expr="string:${object_url}/metadata_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
</type-info>
"""

_BAR_EXPORT = """\
<type-info
   id="%s"
   kind="Scriptable Type Information"
   title="Bar"
   meta_type="Bar Thing"
   icon="bar.png"
   constructor_path="make_bar"
   permission="Add portal content"
   immediate_view="bar_view"
   filter_content_types="True"
   allow_discussion="True"
   global_allow="True" >
  <description>Bar things</description>
  <allowed_content_type>foo</allowed_content_type>
  <aliases>
   <alias from="(Default)" to="bar_view" />
   <alias from="view" to="bar_view" />
  </aliases>
  <action
     action_id="view"
     title="View"
     url_expr="string:${object_url}/bar_view"
     condition_expr=""
     category="object"
     visible="True">
   <permission>View</permission>
  </action>
  <action
     action_id="edit"
     title="Edit"
     url_expr="string:${object_url}/bar_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
  <action
     action_id="contents"
     title="Contents"
     url_expr="string:${object_url}/folder_contents"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Access contents information</permission>
  </action>
  <action
     action_id="metadata"
     title="Metadata"
     url_expr="string:${object_url}/metadata_edit_form"
     condition_expr=""
     category="object"
     visible="True">
   <permission>Modify portal content</permission>
  </action>
</type-info>
"""

class Test_exportTypesTool( _TypeInfoSetup ):

    def test_empty( self ):

        site = self._initSite()
        context = DummyExportContext( site )

        from Products.CMFSetup.typeinfo import exportTypesTool
        exportTypesTool( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'typestool.xml' )
        self._compareDOM( text, _EMPTY_TOOL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        site = self._initSite( _TI_LIST )
        context = DummyExportContext( site )

        from Products.CMFSetup.typeinfo import exportTypesTool
        exportTypesTool( context )

        self.assertEqual( len( context._wrote ), 3 )

        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'typestool.xml' )
        self._compareDOM( text, _NORMAL_TOOL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'types/foo.xml' )
        self._compareDOM( text, _FOO_EXPORT % 'foo' )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 2 ]
        self.assertEqual( filename, 'types/bar.xml' )
        self._compareDOM( text, _BAR_EXPORT % 'bar' )
        self.assertEqual( content_type, 'text/xml' )

    def test_with_filenames( self ):

        site = self._initSite( _TI_LIST_WITH_FILENAME )
        context = DummyExportContext( site )

        from Products.CMFSetup.typeinfo import exportTypesTool
        exportTypesTool( context )

        self.assertEqual( len( context._wrote ), 3 )

        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'typestool.xml' )
        self._compareDOM( text, _FILENAME_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'types/foo_object.xml' )
        self._compareDOM( text, _FOO_EXPORT % 'foo object' )
        self.assertEqual( content_type, 'text/xml' )

        filename, text, content_type = context._wrote[ 2 ]
        self.assertEqual( filename, 'types/bar_object.xml' )
        self._compareDOM( text, _BAR_EXPORT % 'bar object' )
        self.assertEqual( content_type, 'text/xml' )

class Test_importTypesTool( _TypeInfoSetup ):

    def test_empty_default_purge( self ):

        site = self._initSite( _TI_LIST )
        tool = site.portal_types

        self.assertEqual( len( tool.objectIds() ), 2 )

        context = DummyImportContext( site )
        context._files[ 'typestool.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.typeinfo import importTypesTool
        importTypesTool( context )

        self.assertEqual( len( tool.objectIds() ), 0 )

    def test_empty_explicit_purge( self ):

        site = self._initSite( _TI_LIST )
        tool = site.portal_types

        self.assertEqual( len( tool.objectIds() ), 2 )

        context = DummyImportContext( site, True )
        context._files[ 'typestool.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.typeinfo import importTypesTool
        importTypesTool( context )

        self.assertEqual( len( tool.objectIds() ), 0 )

    def test_empty_skip_purge( self ):

        site = self._initSite( _TI_LIST )
        tool = site.portal_types

        self.assertEqual( len( tool.objectIds() ), 2 )

        context = DummyImportContext( site, False )
        context._files[ 'typestool.xml' ] = _EMPTY_TOOL_EXPORT

        from Products.CMFSetup.typeinfo import importTypesTool
        importTypesTool( context )

        self.assertEqual( len( tool.objectIds() ), 2 )

    def test_normal( self ):

        site = self._initSite()
        tool = site.portal_types

        self.assertEqual( len( tool.objectIds() ), 0 )

        context = DummyImportContext( site )
        context._files[ 'typestool.xml' ] = _NORMAL_TOOL_EXPORT
        context._files[ 'types/foo.xml' ] = _FOO_EXPORT % 'foo'
        context._files[ 'types/bar.xml' ] = _BAR_EXPORT % 'bar'

        from Products.CMFSetup.typeinfo import importTypesTool
        importTypesTool( context )

        self.assertEqual( len( tool.objectIds() ), 2 )
        self.failUnless( 'foo' in tool.objectIds() )
        self.failUnless( 'bar' in tool.objectIds() )

    def test_with_filenames_ascii( self ):

        site = self._initSite()
        tool = site.portal_types

        self.assertEqual( len( tool.objectIds() ), 0 )

        context = DummyImportContext( site, encoding='ascii' )
        context._files[ 'typestool.xml' ] = _FILENAME_EXPORT
        context._files[ 'types/foo_object.xml' ] = _FOO_EXPORT % 'foo object'
        context._files[ 'types/bar_object.xml' ] = _BAR_EXPORT % 'bar object'

        from Products.CMFSetup.typeinfo import importTypesTool
        importTypesTool( context )

        self.assertEqual( len( tool.objectIds() ), 2 )
        self.failUnless( 'foo object' in tool.objectIds() )
        self.failUnless( 'bar object' in tool.objectIds() )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( TypeInfoConfiguratorTests ),
        unittest.makeSuite( Test_exportTypesTool ),
        unittest.makeSuite( Test_importTypesTool ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
