import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFCore.tests.base.dummy import \
     DummyTool

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation

class DummyProvider( ActionProviderBase ):

    _actions = [ ActionInformation( id='an_id'
                                  , title='A Title'
                                  , action=''
                                  , condition=''
                                  , permissions=''
                                  , category=''
                                  , visible=0
                                  )
               ]

class ActionProviderBaseTests(TestCase):
    
    def _makeProvider( self ):

        return ActionProviderBase()

    def test_addAction( self ):

        apb = self._makeProvider()
        self.failIf( apb._actions )
        old_actions = apb._actions
        apb.addAction( id='foo'
                     , name='foo_action'
                     , action=''
                     , condition=''
                     , permission=''
                     , category=''
                     )
        self.failUnless( apb._actions )
        self.failIf( apb._actions is old_actions )
        # make sure a blank permission gets stored as an empty tuple
        self.assertEqual( apb._actions[0].permissions, () )

    def test_changeActions( self ):


        apb = DummyTool()
        old_actions = apb._actions

        keys = [ ( 'id_%d', None )
               , ( 'name_%d', None )
               , ( 'action_%d', '' )
               , ( 'condition_%d', '' )
               , ( 'permission_%d', None )
               , ( 'category_%d', None )
               , ( 'visible_%d', None )
               ]

        properties = {}
        for i in range( len( old_actions ) ):
            for key, value in keys:
                token = key % i
                if value is None:
                    value = token
                properties[ token ] = value

        apb.changeActions( properties=properties )

        marker = []
        for i in range( len( apb._actions ) ):

            for key, value in keys:
                attr = key[ : -3 ]

                if value is None:
                    value = key % i

                if attr == 'name':    # WAAAA
                    attr = 'title'

                if attr == 'action':    # WAAAA
                    attr = '_action'

                if attr == 'permission':    # WAAAA
                    attr = 'permissions'
                    value = ( value, )

                attr_value = getattr( apb._actions[i], attr, marker )
                self.assertEqual( attr_value
                                , value
                                , '%s, %s != %s, %s'
                                  % ( attr, attr_value, key, value )  )
        self.failIf( apb._actions is old_actions )

    def test_deleteActions( self ):

        apb = self._makeProvider()
        apb._actions = [ '0', '1', '2' ]  # fake out for testing
        apb.deleteActions( selections=(0,2) )
        self.assertEqual( apb._actions, ['1'] )

    def test_DietersNastySharingBug( self ):

        one = DummyProvider()
        another = DummyProvider()

        def idify( x ): return id( x )

        old_ids = one_ids = map( idify, one.listActions() )
        another_ids = map( idify, another.listActions() )

        self.assertEqual( one_ids, another_ids )

        one.changeActions( { 'id_0'            : 'different_id'
                           , 'name_0'          : 'A Different Title'
                           , 'action_0'        : 'arise_shine'
                           , 'condition_0'     : 'always'
                           , 'permissions_0'   : 'granted'
                           , 'category_0'      : 'quality'
                           , 'visible_0'       : 1
                           } )

        one_ids = map( idify, one.listActions() )
        another_ids = map( idify, another.listActions() )
        self.failIf( one_ids == another_ids )
        self.assertEqual( old_ids, another_ids )

def test_suite():
    return TestSuite((
        makeSuite(ActionProviderBaseTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
