""" Unit tests for type information export import

$Id$
"""

import unittest

from OFS.Folder import Folder

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ModifyPortalContent

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext

class DummyTypesTool( Folder ):

    def __init__( self, type_infos ):

        self._type_infos = type_infos

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

class TypeInfoConfiguratorTests( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.typeinfo import TypeInfoConfigurator
        return TypeInfoConfigurator

    def _initSite( self, type_infos=() ):

        self.root.site = Folder( id='site' )

        self.root.site.portal_types = DummyTypesTool( type_infos )

        return self.root.site

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

    #
    #   XXX:  Design Issue
    #
    #   These tests presume a single, "monolithic" XML file, output for
    #   the whole tool;  while this is doable, it tends to lead to files
    #   which are hard to maintain (for humans).
    #
    #   We should consider breaking them up, with the output for each
    #   type information object in a separate file, all grouped in a
    #   'typeinfo' subdirectory within the export.
    #
    def test_generateToolXML_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateToolXML(), _EMPTY_EXPORT )

    def test_generateToolXML_normal( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )

    def test_generateTypeXML_FTI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateTypeXML( 'foo' ), _FOO_EXPORT )

    def test_generateTypeXML_STI( self ):

        site = self._initSite( _TI_LIST )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateTypeXML( 'bar' ), _BAR_EXPORT )



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

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
</types-tool>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<types-tool>
 <type>foo</type>
 <type>bar</type>
</types-tool>
"""

_FOO_EXPORT = """\
<type-info
   id="foo"
   kind="Factory-based Type Information"
   title="Foo"
   meta_type="Foo Thing"
   icon="foo.png"
   product="CMFSetup"
   factory="addFoo"
   immediate_view="foo_view"
   filter_content_types="False"
   allowed_content_types=""
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
     action_expr="string:${object_url}/foo_view"
     condition=""
     permissions="View"
     category="object"
     visible="True"
     />
  <action
     action_id="edit"
     title="Edit"
     action_expr="string:${object_url}/foo_edit_form"
     condition=""
     permissions="Modify portal content"
     category="object"
     visible="True"
     />
  <action
     action_id="metadata"
     title="Metadata"
     action_expr="string:${object_url}/metadata_edit_form"
     condition=""
     permissions="Modify portal content"
     category="object"
     visible="True"
     />
</type-info>
"""

_BAR_EXPORT = """\
<type-info
   id="bar"
   kind="Scriptable Type Information"
   title="Bar"
   meta_type="Bar Thing"
   icon="bar.png"
   constructor_path="make_bar"
   permission="Add portal content"
   immediate_view="bar_view"
   filter_content_types="True"
   allowed_content_types="foo"
   allow_discussion="True"
   global_allow="True" >
  <description>Bar things</description>
  <aliases>
   <alias from="(Default)" to="bar_view" />
   <alias from="view" to="bar_view" />
  </aliases>
  <action
     action_id="view"
     title="View"
     action_expr="string:${object_url}/bar_view"
     condition=""
     permissions="View"
     category="object"
     visible="True"
     />
  <action
     action_id="edit"
     title="Edit"
     action_expr="string:${object_url}/bar_edit_form"
     condition=""
     permissions="Modify portal content"
     category="object"
     visible="True"
     />
  <action
     action_id="contents"
     title="Contents"
     action_expr="string:${object_url}/folder_contents"
     condition=""
     permissions="Access contents information"
     category="object"
     visible="True"
     />
  <action
     action_id="metadata"
     title="Metadata"
     action_expr="string:${object_url}/metadata_edit_form"
     condition=""
     permissions="Modify portal content"
     category="object"
     visible="True"
     />
</type-info>
"""


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( TypeInfoConfiguratorTests ),
        #unittest.makeSuite( Test_exportRolemap ),
        #unittest.makeSuite( Test_importRolemap ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
