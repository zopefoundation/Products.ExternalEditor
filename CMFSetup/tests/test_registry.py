""" Registry unit tests.

$Id$
"""
import unittest
import os

from Products.CMFCore.tests.base.testcase import SecurityRequestTest

class SetupStepRegistryTests( SecurityRequestTest ):

    def _getTargetClass( self ):

        from Products.CMFSetup.registry import SetupStepRegistry
        return SetupStepRegistry

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def _compareDOM( self, found_text, expected_text ):

        from xml.dom.minidom import parseString
        found = parseString( found_text )
        expected = parseString( expected_text )
        self.assertEqual( found.toxml(), expected.toxml() )

    def test_empty( self ):

        registry = self._makeOne()

        self.assertEqual( len( registry.listSteps() ), 0 )
        self.assertEqual( len( registry.listStepMetadata() ), 0 )
        self.assertEqual( len( registry.sortSteps() ), 0 )

    def test_getStep_nonesuch( self ):

        registry = self._makeOne()

        self.assertEqual( registry.getStep( 'nonesuch' ), None )
        self.assertEqual( registry.getStep( 'nonesuch' ), None )
        default = object()
        self.failUnless( registry.getStepMetadata( 'nonesuch'
                                                 , default ) is default )
        self.failUnless( registry.getStep( 'nonesuch', default ) is default )
        self.failUnless( registry.getStepMetadata( 'nonesuch'
                                                 , default ) is default )

    def test_registerStep_single( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , description='One small step'
                             )

        steps = registry.listSteps()
        self.assertEqual( len( steps ), 1 )
        self.failUnless( 'one' in steps )

        sorted = registry.sortSteps()
        self.assertEqual( len( sorted ), 1 )
        self.assertEqual( sorted[ 0 ], 'one' )

        self.assertEqual( registry.getStep( 'one' ), ONE_FUNC )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1' )
        self.assertEqual( info[ 'callable' ], ONE_FUNC_NAME )
        self.assertEqual( info[ 'dependencies' ], ( 'two', 'three' ) )
        self.assertEqual( info[ 'description' ], 'One small step' )

        info_list = registry.listStepMetadata()
        self.assertEqual( len( info_list ), 1 )
        self.assertEqual( info, info_list[ 0 ] )

    def test_registerStep_conflict( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , description='One small step'
                             )

        self.assertRaises( KeyError
                         , registry.registerStep
                         , id='one'
                         , version='0'
                         , callable=ONE_FUNC
                         , dependencies=( 'two', 'three' )
                         , description='One small step'
                         )

        self.assertRaises( KeyError
                         , registry.registerStep
                         , id='one'
                         , version='1'
                         , callable=ONE_FUNC
                         , dependencies=( 'two', 'three' )
                         , description='One small step'
                         )

    def test_registerStep_replacement( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , description='One small step'
                             )

        registry.registerStep( id='one'
                             , version='1.1'
                             , callable=ONE_FUNC
                             , dependencies=()
                             , description='One small step'
                             )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1.1' )
        self.assertEqual( info[ 'dependencies' ], () )
        self.assertEqual( info[ 'description' ], 'One small step' )

    def test_registerStep_multiple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=()
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=()
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=()
                             , description='Gimme three steps'
                             )

        steps = registry.listSteps()
        self.assertEqual( len( steps ), 3 )
        self.failUnless( 'one' in steps )
        self.failUnless( 'two' in steps )
        self.failUnless( 'three' in steps )

    def test_sortStep_simple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', )
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=()
                             , description='Texas two step'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 2 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )

        self.failUnless( 0 <= two < one )

    def test_sortStep_chained( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', )
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=( 'three', )
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=()
                             , description='Gimme three steps'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 3 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )

        self.failUnless( 0 <= three < two < one )

    def test_sortStep_complex( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', )
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=( 'four', )
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=( 'four', )
                             , description='Gimme three steps'
                             )

        registry.registerStep( id='four'
                             , version='4'
                             , callable=FOUR_FUNC
                             , dependencies=()
                             , description='Four step program'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 4 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )
        four = steps.index( 'four' )

        self.failUnless( 0 <= four < two < one )
        self.failUnless( 0 <= four < three )

    def test_sortStep_equivalence( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=( 'four', )
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=( 'four', )
                             , description='Gimme three steps'
                             )

        registry.registerStep( id='four'
                             , version='4'
                             , callable=FOUR_FUNC
                             , dependencies=()
                             , description='Four step program'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 4 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )
        four = steps.index( 'four' )

        self.failUnless( 0 <= four < two < one )
        self.failUnless( 0 <= four < three < one )

    def test_checkComplete_simple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', )
                             , description='One small step'
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'one', 'two' ) in incomplete )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=()
                             , description='Texas two step'
                             )

        self.assertEqual( len( registry.checkComplete() ), 0 )

    def test_checkComplete_double( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , description='One small step'
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 2 )
        self.failUnless( ( 'one', 'two' ) in incomplete )
        self.failUnless( ( 'one', 'three' ) in incomplete )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=()
                             , description='Texas two step'
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'one', 'three' ) in incomplete )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=()
                             , description='Gimme three steps'
                             )

        self.assertEqual( len( registry.checkComplete() ), 0 )

        registry.registerStep( id='two'
                             , version='2.1'
                             , callable=TWO_FUNC
                             , dependencies=( 'four', )
                             , description='Texas two step'
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'two', 'four' ) in incomplete )

    def test_export_empty( self ):

        registry = self._makeOne().__of__( self.root )

        xml = registry.exportAsXML()

        self._compareDOM( registry.exportAsXML(), _EMPTY_EXPORT )

    def test_export_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=()
                             , description='One small step'
                             )

        self._compareDOM( registry.exportAsXML(), _SINGLE_EXPORT )

    def test_export_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=( 'two', )
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=( 'three', )
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , callable=THREE_FUNC
                             , dependencies=()
                             , description='Gimme three steps'
                             )

        self._compareDOM( registry.exportAsXML(), _ORDERED_EXPORT )

    def test_import_empty( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , callable=ONE_FUNC
                             , dependencies=()
                             , description='One small step'
                             )

        registry.importFromXML( _EMPTY_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 0 )
        self.assertEqual( len( registry.listStepMetadata() ), 0 )
        self.assertEqual( len( registry.sortSteps() ), 0 )

    def test_import_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='two'
                             , version='2'
                             , callable=TWO_FUNC
                             , dependencies=()
                             , description='Texas two step'
                             )

        registry.importFromXML( _SINGLE_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 1 )
        self.failUnless( 'one' in registry.listSteps() )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1' )
        self.assertEqual( info[ 'dependencies' ], () )
        self.failUnless( 'One small step' in info[ 'description' ] )

    def test_import_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.importFromXML( _ORDERED_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 3 )
        self.failUnless( 'one' in registry.listSteps() )
        self.failUnless( 'two' in registry.listSteps() )
        self.failUnless( 'three' in registry.listSteps() )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 3 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )

        self.failUnless( 0 <= three < two < one )

#
#   Dummy callables
#
def ONE_FUNC( context ): pass
def TWO_FUNC( context ): pass
def THREE_FUNC( context ): pass
def FOUR_FUNC( context ): pass

ONE_FUNC_NAME = '%s.%s' % ( __name__, ONE_FUNC.__name__ )
TWO_FUNC_NAME = '%s.%s' % ( __name__, TWO_FUNC.__name__ )
THREE_FUNC_NAME = '%s.%s' % ( __name__, THREE_FUNC.__name__ )
FOUR_FUNC_NAME = '%s.%s' % ( __name__, FOUR_FUNC.__name__ )

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
</setup-steps>
"""

_SINGLE_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
 <setup-step id="one"
             version="1"
             callable="%s">
  One small step
 </setup-step>
</setup-steps>
""" % ( ONE_FUNC_NAME, )

_ORDERED_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
 <setup-step id="three"
             version="3"
             callable="%s">
  Gimme three steps
 </setup-step>
 <setup-step id="two"
             version="2"
             callable="%s">
  <dependency step="three" />
  Texas two step
 </setup-step>
 <setup-step id="one"
             version="1"
             callable="%s">
  <dependency step="two" />
  One small step
 </setup-step>
</setup-steps>
""" % ( THREE_FUNC_NAME, TWO_FUNC_NAME, ONE_FUNC_NAME )



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SetupStepRegistryTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
