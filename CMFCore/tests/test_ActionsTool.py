import Zope, unittest
from Products.CMFCore.ActionsTool import *
from Products.CMFDefault.URLTool import *
import ZPublisher.HTTPRequest

class ActionsToolTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        root = self.root = self.connection.root()[ 'Application' ]

        env = { 'SERVER_NAME' : 'http://localhost'
              , 'SERVER_PORT' : '80'
              }
        root.REQUEST = ZPublisher.HTTPRequest.HTTPRequest( None, env, None )
        
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject('foo', URLTool() )
        self.tool = root.portal_actions
        self.ut = root.foo
        self.tool.action_providers = ('portal_actions',)

    def test_actionProviders(self):
        tool = self.tool
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def test_addActionProvider(self):
        tool = self.tool
        tool.addActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions', 'foo'))

    def test_delActionProvider(self):
        tool = self.tool
        tool.deleteActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions',))

    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionsToolTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
