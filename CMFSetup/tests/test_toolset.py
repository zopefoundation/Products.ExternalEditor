""" Tools importer unit tests.

$Id$
"""
import unittest
import os

from OFS.Folder import Folder

from Products.CMFSetup.tests.common import BaseRegistryTests

#==============================================================================
#   Dummy handlers
#==============================================================================
def ONE_FUNC( context ): pass
def TWO_FUNC( context ): pass
def THREE_FUNC( context ): pass
def FOUR_FUNC( context ): pass

ONE_FUNC_NAME = '%s.%s' % ( __name__, ONE_FUNC.__name__ )
TWO_FUNC_NAME = '%s.%s' % ( __name__, TWO_FUNC.__name__ )
THREE_FUNC_NAME = '%s.%s' % ( __name__, THREE_FUNC.__name__ )
FOUR_FUNC_NAME = '%s.%s' % ( __name__, FOUR_FUNC.__name__ )


#==============================================================================
#   SSR tests
#==============================================================================
class TestToolInitializer( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.toolset import ToolInitializer
        return ToolInitializer

    def _initSite( self, foo=2, bar=2 ):

        self.root.site = Folder( id='site' )
        site = self.root.site

        return site

    def test_empty( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        self.assertEqual( len( configurator.listForbiddenTools() ), 0 )
        self.assertEqual( len( configurator.listRequiredTools() ), 0 )
        self.assertEqual( len( configurator.listRequiredToolInfo() ), 0 )

        self.assertRaises( KeyError
                         , configurator.getRequiredToolInfo, 'nonesuch' )

    def test_addForbiddenTool_multiple( self ):

        VERBOTTEN = ( 'foo', 'bar', 'bam' )

        site = self._initSite()
        configurator = self._makeOne( site )

        for verbotten in VERBOTTEN:
            configurator.addForbiddenTool( verbotten )

        self.assertEqual( len( configurator.listForbiddenTools() )
                        , len( VERBOTTEN ) )

        for verbotten in configurator.listForbiddenTools():
            self.failUnless( verbotten in VERBOTTEN )

    def test_addForbiddenTool_duplicate( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        configurator.addForbiddenTool( 'once' )

        self.assertRaises( KeyError, configurator.addForbiddenTool, 'once' )

    def test_addForbiddenTool_but_required( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        configurator.addRequiredTool( 'required', 'some.dotted.name' )

        self.assertRaises( ValueError
                         , configurator.addForbiddenTool, 'required' )

    def test_addRequiredTool_multiple( self ):

        REQUIRED = ( ( 'one', 'path.to.one' )
                   , ( 'two', 'path.to.two' )
                   , ( 'three', 'path.to.three' )
                   )

        site = self._initSite()
        configurator = self._makeOne( site )

        for tool_id, dotted_name in REQUIRED:
            configurator.addRequiredTool( tool_id, dotted_name )

        self.assertEqual( len( configurator.listRequiredTools() )
                        , len( REQUIRED ) )

        for id in [ x[0] for x in REQUIRED ]:
            self.failUnless( id in configurator.listRequiredTools() )

        self.assertEqual( len( configurator.listRequiredToolInfo() )
                        , len( REQUIRED ) )

        for tool_id, dotted_name in REQUIRED:
            info = configurator.getRequiredToolInfo( tool_id )
            self.assertEqual( info[ 'id' ], tool_id )
            self.assertEqual( info[ 'class' ], dotted_name )

    def test_addRequiredTool_duplicate( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        configurator.addRequiredTool( 'required', 'some.dotted.name' )

        self.assertRaises( KeyError
                         , configurator.addRequiredTool
                         , 'required'
                         , 'another.name'
                         )

    def test_addRequiredTool_but_forbidden( self ):

        site = self._initSite()
        configurator = self._makeOne( site )

        configurator.addForbiddenTool( 'forbidden' )

        self.assertRaises( ValueError
                         , configurator.addRequiredTool
                         , 'forbidden'
                         , 'a.name'
                         )

    def test_parseXML_empty( self ):

        site = self._initSite( 0, 0 )
        configurator = self._makeOne( site )

        configurator.parseXML( _EMPTY_IMPORT_XML )

        self.assertEqual( len( configurator.listForbiddenTools() ), 0 )
        self.assertEqual( len( configurator.listRequiredTools() ), 0 )

    def test_parseXML_normal( self ):

        site = self._initSite( 0, 0 )
        configurator = self._makeOne( site )

        configurator.parseXML( _NORMAL_IMPORT_XML )

        self.assertEqual( len( configurator.listForbiddenTools() ), 1 )
        self.failUnless( 'doomed' in configurator.listForbiddenTools() )

        self.assertEqual( len( configurator.listRequiredTools() ), 2 )

        self.failUnless( 'mandatory' in configurator.listRequiredTools() )
        info = configurator.getRequiredToolInfo( 'mandatory' )
        self.assertEqual( info[ 'class' ], 'path.to.one' )

        self.failUnless( 'obligatory' in configurator.listRequiredTools() )
        info = configurator.getRequiredToolInfo( 'obligatory' )
        self.assertEqual( info[ 'class' ], 'path.to.another' )

    def test_parseXML_confused( self ):

        site = self._initSite( 0, 0 )
        configurator = self._makeOne( site )

        self.assertRaises( ValueError
                         , configurator.parseXML, _CONFUSED_IMPORT_XML )


_EMPTY_IMPORT_XML = """\
<?xml version="1.0"?>
<tool-setup>
</tool-setup>
"""

_NORMAL_IMPORT_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="doomed" />
 <required tool_id="mandatory" class="path.to.one" />
 <required tool_id="obligatory" class="path.to.another" />
</tool-setup>
"""

_CONFUSED_IMPORT_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="confused" />
 <required tool_id="confused" class="path.to.one" />
</tool-setup>
"""

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( TestToolInitializer ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
