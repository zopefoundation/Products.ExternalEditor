import unittest

class DummyAction:
    def __init__( self, **kw ):
        self.__dict__.update( kw )

class ActionProviderBaseTests(unittest.TestCase):
    
    def _makeProvider( self ):

        from Products.CMFCore.ActionProviderBase import ActionProviderBase
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

    def test_changeActions( self ):

        from Products.CMFCore.ActionProviderBase import ActionProviderBase

        class DummyTool( ActionProviderBase ):
            _actions = [ DummyAction()
                       , DummyAction()
                       ]

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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionProviderBaseTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
