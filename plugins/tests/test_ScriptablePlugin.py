import unittest
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from Interface import Interface

class IFaux( Interface ):

    def faux_method():
        pass

class IFauxTwo( Interface ):

    def two_method():
        pass

class DummyPluginRegistry( Folder ):

    def listPluginIds( self, interface ):
        return ()

    def _getInterfaceFromName( self, name ):
        if name == 'IFaux':
            return IFaux
        if name == 'IFauxTwo':
            return IFauxTwo

class ScriptablePluginTests( unittest.TestCase ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.ScriptablePlugin \
            import ScriptablePlugin

        return ScriptablePlugin

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def test_empty( self ):

        scriptable_plugin = self._makeOne()
        self.assertEqual( len(scriptable_plugin.__implements__), 2 )

    def test_withTwo( self ):

        parent = Folder()
        parent._setObject( 'plugins', DummyPluginRegistry() )

        scriptable_plugin = self._makeOne().__of__(parent)

        faux_method = SimpleItem( 'faux_method' )
        two_method = SimpleItem( 'two_method' )

        scriptable_plugin._setObject( 'faux_method', faux_method )
        scriptable_plugin._setObject( 'two_method', two_method )

        scriptable_plugin.manage_updateInterfaces( ['IFaux', 'IFauxTwo'] )

        self.assertEqual( len(scriptable_plugin.__implements__), 4 )
    
    def test_withTwoOnlyOneWired( self ):

        parent = Folder()
        parent._setObject( 'plugins', DummyPluginRegistry() )

        scriptable_plugin = self._makeOne().__of__(parent)

        faux_method = SimpleItem( 'faux_method' )
        whatever = SimpleItem( 'whatever' )

        scriptable_plugin._setObject( 'faux_method', faux_method )
        scriptable_plugin._setObject( 'whatever', whatever )

        scriptable_plugin.manage_updateInterfaces( ['IFaux',] )

        self.assertEqual( len(scriptable_plugin.__implements__), 3 )

    def test_withTwoMinusOne( self ):

        parent = Folder()
        parent._setObject( 'plugins', DummyPluginRegistry() )

        scriptable_plugin = self._makeOne().__of__(parent)

        faux_method = SimpleItem( 'faux_method' )
        two_method = SimpleItem( 'two_method' )

        scriptable_plugin._setObject( 'faux_method', faux_method )
        scriptable_plugin._setObject( 'two_method', two_method )

        scriptable_plugin.manage_updateInterfaces( ['IFaux', 'IFauxTwo'] )

        scriptable_plugin._delObject( 'two_method' )

        self.assertEqual( len(scriptable_plugin.__implements__), 3 )

