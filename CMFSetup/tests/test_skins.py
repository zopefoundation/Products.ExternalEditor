""" Unit tests for CMFSetup skins configurator

$Id$
"""

import unittest

from OFS.Folder import Folder
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext

class DummySkinsTool( Folder ):

    def __init__( self, selections={} ):

        self._selections = selections

    def _getSelections( self ):

        return self._selections

    def getSkinPaths( self ):

        result = list( self._selections.items() )
        result.sort()
        return result


class SkinsToolConfiguratorTests( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.skins import SkinsToolConfigurator
        return SkinsToolConfigurator

    def _initSite( self, selections={} ):

        self.root.site = Folder( id='site' )
        self.root.site.portal_skins = DummySkinsTool( selections )
        return self.root.site

    def test_listSkinPaths_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        self.assertEqual( len( configurator.listSkinPaths() ), 0 )

    def test_listSkinPaths_with_selections( self ):

        site = self._initSite( { 'a' : '/a/b/c', 'b' : '/d/e/f' } )
        configurator = self._makeOne( site )

        self.assertEqual( len( configurator.listSkinPaths() ), 2 )
        folders = configurator.listSkinPaths()

        self.assertEqual( folders[ 0 ][ 'id' ], 'a' )
        self.assertEqual( folders[ 0 ][ 'path' ], '/a/b/c' )

        self.assertEqual( folders[ 1 ][ 'id' ], 'b' )
        self.assertEqual( folders[ 1 ][ 'path' ], '/d/e/f' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SkinsToolConfiguratorTests ),
        #unittest.makeSuite( Test_exportSkinsTool ),
        #unittest.makeSuite( Test_importSkinsTool ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
