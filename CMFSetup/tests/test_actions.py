""" CMFSetup action provider export / import unit tests

$Id$
"""

import unittest

from Acquisition import Implicit
from Acquisition import aq_parent
from OFS.Folder import Folder
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.interfaces.portal_actions \
    import ActionProvider as IActionProvider

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext

class DummyTool( Folder, ActionProviderBase ):

    __implements__ = ( IActionProvider, )

class DummyUser( Implicit ):

    def getId( self ):
        return 'dummy'

class DummyMembershipTool( DummyTool ):

    def isAnonymousUser( self ):
        return False

    def getAuthenticatedMember( self ):
        return DummyUser().__of__( aq_parent( self ) )

class DummyActionsTool( DummyTool ):

    def __init__( self ):

        self._providers = []

    def addActionProvider( self, provider_name ):

        self._providers.append( provider_name )

    def listActionProviders( self ):

        return self._providers[:]

    def deleteActionProvider( self, provider_name ):

        self._providers = [ x for x in self._providers if x != provider_name ]

class _ActionSetup( BaseRegistryTests ):

    def _initSite( self, foo=2, bar=2 ):

        self.root.site = Folder( id='site' )
        site = self.root.site

        site.portal_membership = DummyMembershipTool()

        site.portal_actions = DummyActionsTool()
        site.portal_actions.addActionProvider( 'portal_actions' )

        if foo > 0:
            site.portal_foo = DummyTool()

        if foo > 1:
            site.portal_foo.addAction( id='foo'
                                    , name='Foo'
                                    , action='foo'
                                    , condition='python:1'
                                    , permission=()
                                    , category='dummy'
                                    , visible=1
                                    )
            site.portal_actions.addActionProvider( 'portal_foo' )

        if bar > 0:
            site.portal_bar = DummyTool()

        if bar > 1:
            site.portal_bar.addAction( id='bar'
                                    , name='Bar'
                                    , action='bar'
                                    , condition='python:0'
                                    , permission=( 'Manage portal', )
                                    , category='dummy'
                                    , visible=0
                                    )
            site.portal_actions.addActionProvider( 'portal_bar' )

        return site

class ActionProvidersConfiguratorTests( _ActionSetup ):

    def _getTargetClass( self ):

        from Products.CMFSetup.actions import ActionProvidersConfigurator
        return ActionProvidersConfigurator

    def test_listProviderInfo_normal( self ):

        site = self._initSite()

        EXPECTED = [ { 'id' : 'portal_actions'
                     , 'actions' : []
                     }
                   , { 'id' : 'portal_foo'
                     , 'actions' : [ { 'id' : 'foo'
                                     , 'title' : 'Foo'
                                     , 'description' : ''
                                     , 'action' : 'string:${object_url}/foo'
                                     , 'condition' : 'python:1'
                                     , 'permissions' : ()
                                     , 'category' : 'dummy'
                                     , 'visible' : True
                                     }
                                   ]
                     }
                   , { 'id' : 'portal_bar'
                     , 'actions' : [ { 'id' : 'bar'
                                     , 'title' : 'Bar'
                                     , 'description' : ''
                                     , 'action' : 'string:${object_url}/bar'
                                     , 'condition' : 'python:0'
                                     , 'permissions' : ('Manage portal',)
                                     , 'category' : 'dummy'
                                     , 'visible' : False
                                     }
                                   ]
                     }
                   ]

        configurator = self._makeOne( site )

        info_list = configurator.listProviderInfo()
        self.assertEqual( len( info_list ), len( EXPECTED ) )

        for found, expected in zip( info_list, EXPECTED ):
            self.assertEqual( found, expected )

    def test_generateXML_empty( self ):

        site = self._initSite( 0, 0 )
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateXML(), _EMPTY_EXPORT )

    def test_generateXML_normal( self ):

        site = self._initSite()
        configurator = self._makeOne( site ).__of__( site )
        self._compareDOM( configurator.generateXML(), _NORMAL_EXPORT )


    def test_parseXML_empty( self ):

        site = self._initSite( 0, 0 )
        configurator = self._makeOne( site )

        info_list = configurator.parseXML( _EMPTY_EXPORT )

        self.assertEqual( len( info_list ), 1 )

        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'portal_actions' )
        self.assertEqual( len( info[ 'actions' ] ), 0 )

    def test_parseXML_normal( self ):

        site = self._initSite( 1, 1 )

        configurator = self._makeOne( site )
        info_list = configurator.parseXML( _NORMAL_EXPORT )

        self.assertEqual( len( info_list ), 3 )

        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'portal_actions' )
        self.assertEqual( len( info[ 'actions' ] ), 0 )

        info = info_list[ 1 ]
        self.assertEqual( info[ 'id' ], 'portal_foo' )
        self.assertEqual( len( info[ 'actions' ] ), 1 )

        action = info[ 'actions' ][ 0 ]
        self.assertEqual( action[ 'id' ], 'foo' )
        self.assertEqual( action[ 'title' ], 'Foo' )
        self.assertEqual( action[ 'action' ]
                        , 'string:${object_url}/foo' )
        self.assertEqual( action[ 'condition' ], 'python:1' )
        self.assertEqual( action[ 'permissions' ], () )
        self.assertEqual( action[ 'category' ], 'dummy' )
        self.assertEqual( action[ 'visible' ], True )

        info = info_list[ 2 ]
        self.assertEqual( info[ 'id' ], 'portal_bar' )
        self.assertEqual( len( info[ 'actions' ] ), 1 )

        action = info[ 'actions' ][ 0 ]
        self.assertEqual( action[ 'id' ], 'bar' )
        self.assertEqual( action[ 'title' ], 'Bar' )
        self.assertEqual( action[ 'action' ]
                        , 'string:${object_url}/bar' )
        self.assertEqual( action[ 'condition' ], 'python:0' )
        self.assertEqual( action[ 'permissions' ], ('Manage portal',) )
        self.assertEqual( action[ 'category' ], 'dummy' )
        self.assertEqual( action[ 'visible' ], False )



_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<actions-tool>
 <action-provider id="portal_actions">
 </action-provider>
</actions-tool>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<actions-tool>
 <action-provider id="portal_actions">
 </action-provider>
 <action-provider id="portal_foo">
  <action action_id="foo"
          title="Foo"
          url_expr="string:${object_url}/foo"
          condition_expr="python:1"
          category="dummy"
          visible="True">
  </action>
</action-provider>
 <action-provider id="portal_bar">
  <action action_id="bar"
          title="Bar"
          url_expr="string:${object_url}/bar"
          condition_expr="python:0"
          category="dummy"
          visible="False">
   <permission>Manage portal</permission>
  </action>
 </action-provider>
</actions-tool>
"""


class Test_exportActionProviders( _ActionSetup ):

    def test_unchanged( self ):

        site = self._initSite( 0, 0 )
        context = DummyExportContext( site )

        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'actions.xml' )
        self._compareDOM( text, _EMPTY_EXPORT )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        site = self._initSite()

        context = DummyExportContext( site )

        from Products.CMFSetup.actions import exportActionProviders
        exportActionProviders( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'actions.xml' )
        self._compareDOM( text, _NORMAL_EXPORT )
        self.assertEqual( content_type, 'text/xml' )


class Test_importActionProviders( _ActionSetup ):

    def test_empty_default_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )

    def test_empty_explicit_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site, True )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

    def test_empty_skip_purge( self ):

        site = self._initSite( 2, 0 )
        atool = site.portal_actions

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site, False )
        context._files[ 'actions.xml' ] = _EMPTY_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 2 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

    def test_normal( self ):

        site = self._initSite( 1, 1 )
        atool = site.portal_actions
        foo = site.portal_foo
        bar = site.portal_bar

        self.assertEqual( len( atool.listActionProviders() ), 1 )
        self.failIf( 'portal_foo' in atool.listActionProviders() )
        self.failIf( foo.listActions() )
        self.failIf( 'portal_bar' in atool.listActionProviders() )
        self.failIf( bar.listActions() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

        context = DummyImportContext( site )
        context._files[ 'actions.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 3 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( foo.listActions() )
        self.failUnless( 'portal_bar' in atool.listActionProviders() )
        self.failUnless( bar.listActions() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )

    def test_normal_encode_as_ascii( self ):

        site = self._initSite( 1, 1 )
        atool = site.portal_actions
        foo = site.portal_foo
        bar = site.portal_bar

        context = DummyImportContext( site, encoding='ascii' )
        context._files[ 'actions.xml' ] = _NORMAL_EXPORT

        from Products.CMFSetup.actions import importActionProviders
        importActionProviders( context )

        self.assertEqual( len( atool.listActionProviders() ), 3 )
        self.failUnless( 'portal_foo' in atool.listActionProviders() )
        self.failUnless( foo.listActions() )
        self.failUnless( 'portal_bar' in atool.listActionProviders() )
        self.failUnless( bar.listActions() )
        self.failUnless( 'portal_actions' in atool.listActionProviders() )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( ActionProvidersConfiguratorTests ),
        unittest.makeSuite( Test_exportActionProviders ),
        unittest.makeSuite( Test_importActionProviders ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
