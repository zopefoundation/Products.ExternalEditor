import Zope
import unittest
import OFS.Folder, OFS.SimpleItem
from AccessControl import SecurityManager
from Products.CMFCore.TypesTool import *
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.PortalFolder import *
import ZPublisher.HTTPRequest

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate(self, accessed, container, name, value, context, roles,
                 *args, **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        return 1

class DummyContent( PortalContent, OFS.SimpleItem.Item ):
    """
    """
    meta_type = 'Dummy'

def addDummy( self, id ):
    """
    """
    self._setObject( id, DummyContent() )

def extra_meta_types():
    return (  { 'name' : 'Dummy', 'action' : 'manage_addFolder' }, )

class TypesToolTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        root = self.root = Zope.app()

        env = { 'SERVER_NAME' : 'http://localhost'
              , 'SERVER_PORT' : '80'
              }
        root.REQUEST = ZPublisher.HTTPRequest.HTTPRequest( None, env, None )
        
        root.addDummy = addDummy

        root._setObject( 'portal_types', TypesTool() )
        tool = root.portal_types
        FTI = FactoryTypeInformation
        tool._setObject( 'Dummy'
                       , FTI( 'Dummy'
                            , meta_type=DummyContent.meta_type
                            , product='OFSP'
                            , factory='addDTMLDocument'
                            )
                       )
    
    def tearDown( self ):
        get_transaction().abort()

    def test_otherFolderTypes( self ):
        """
            Does 'invokeFactory' work when invoked from non-PortalFolder?
        """
        self.root._setObject( 'portal', PortalFolder( 'portal', '' ) )
        portal = self.root.portal
        portal._setObject( 'normal', OFS.Folder.Folder( 'normal', '' ) )
        normal = portal.normal

        normal.invokeFactory( 'Dummy', 'dummy' )
        assert 'dummy' not in portal.objectIds()
        assert 'dummy' in normal.objectIds()



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TypesToolTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
