from Acquisition import Implicit, aq_inner, aq_parent
from OFS.SimpleItem import Item
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.TypesTool import TypeInformation
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.ActionProviderBase import ActionProviderBase


class DummyObject(Implicit):
    """
    A dummy callable object.
    Comes with getIcon and restrictedTraverse
    methods.
    """
    def __init__(self, id='dummy',**kw):
        self.id = id
        self.__dict__.update( kw )
        
    def __str__(self):
        return self.id
    
    def __call__(self):
        return self.id

    def restrictedTraverse( self, path ):
        return path and getattr( self, path ) or self

    def getIcon( self, relative=0 ):
        return 'Site: %s' % relative
    
    def getId(self):
        return self.id


class DummyContent( PortalContent, Item ):
    """
    A Dummy piece of PortalContent
    """
    meta_type = 'Dummy'
    portal_type = 'Dummy Content'
    url = 'foo_url'
    after_add_called = before_delete_called = 0

    def __init__( self, id='dummy', *args, **kw ):
        self.id = id
        self._args = args
        self._kw = {}
        self._kw.update( kw )

        self.reset()
        self.catalog = kw.get('catalog',0)
        self.url = kw.get('url',None)

    def manage_afterAdd( self, item, container ):
        self.after_add_called = 1
        if self.catalog:
            PortalContent.manage_afterAdd( self, item, container )

    def manage_beforeDelete( self, item, container ):
        self.before_delete_called = 1
        if self.catalog:
            PortalContent.manage_beforeDelete( self, item, container )
    
    def absolute_url(self):
       return self.url

    def reset( self ):
        self.after_add_called = self.before_delete_called = 0

    # Make sure normal Database export/import stuff doesn't trip us up.
    def _getCopy( self, container ):        
        return DummyContent( self.id, catalog=self.catalog )

    def _safe_get(self,attr):
        if self.catalog:
            return getattr(self,attr,'')
        else:
            return getattr(self,attr)

    def Title( self ):
        return self.title

    def Creator( self ):
        return self._safe_get('creator')

    def Subject( self ):
        return self._safe_get('subject')

    def Description( self ):
        return self._safe_get('description')

    def created( self ):
        return self._safe_get('created_date')

    def modified( self ):
        return self._safe_get('modified_date')
    
    def Type( self ):
        return 'Dummy Content Title'

def addDummy( self, id ):
    """
    Constructor method for DummyContent
    """
    self._setObject( id, DummyContent() )

class DummyFactory:
    """
    Dummy Product Factory
    """
    def __init__( self, folder ):
        self._folder = folder

    def addFoo( self, id, *args, **kw ):
        if self._folder._prefix:
            id = '%s_%s' % ( self._folder._prefix, id )
        foo = apply( DummyContent, ( id, ) + args, kw )
        self._folder._setOb( id, foo )
        if self._folder._prefix:
            return id

    __roles__ = ( 'FooAdder', )
    __allow_access_to_unprotected_subobjects__ = { 'addFoo' : 1 }


class DummyTypeInfo(TypeInformation):
    """ Dummy class of type info object """
    meta_type = "Dummy Test Type Info"

DummyFTI = FTI( 'Dummy Content'
              , title='Dummy Content Title'
              , meta_type=DummyContent.meta_type
              , product='CMFDefault'
              , factory='addDocument'
              , actions= ( { 'name'          : 'View'
                           , 'action'        : 'string:view'
                           , 'permissions'   : ( 'View', )
                           }
                         , { 'name'          : 'View2'
                           , 'action'        : 'string:view2'
                           , 'permissions'   : ( 'View', )
                           }
                         , { 'name'          : 'Edit'
                           , 'action'        : 'string:edit'
                           , 'permissions'   : ( 'forbidden permission',)
                           }
                         )
              )

class DummyFolder( Implicit ):
    """
        Dummy Container for testing
    """
    def __init__( self, fake_product=0, prefix='' ):
        self._prefix = prefix

        if fake_product:
            self.manage_addProduct = { 'FooProduct' : DummyFactory( self ) }

        self._objects = {}

    def _setOb( self, id, obj ):
        self._objects[id] = obj

    def _getOb( self, id ):
        return self._objects[id]

    def _setObject(self,id,object):
        setattr(self,id,object)


class DummyUserFolder(DummyFolder):
    def __init__(self):
        self._setObject( 'user_foo', DummyObject(id='user_foo') )
        self._setObject( 'user_bar', DummyObject(id='user_bar') )
    def getUsers(self):
        pass
    def getUser(self, name):
        return getattr(self, name, None)
    def getUserById(self, id, default=None):
        return self.getUser(id)


class DummyTool(Implicit,ActionProviderBase):
    """
    This is a Dummy Tool that behaves as a
    a MemberShipTool, a URLTool and an
    Action Provider
    """

    _actions = ( DummyObject()
               , DummyObject()
               )

    root = 'DummyTool'
    
    def __init__(self, anon=1):
        self.anon = anon 

    def isAnonymousUser(self):
        return self.anon 

    def getAuthenticatedMember(self):
        return "member"
  
    def __call__( self ):
        return self.root

    getPortalPath = __call__

    def getPortalObject( self ):
        return aq_parent( aq_inner( self ) )

    def getIcon( self, relative=0 ):
        return 'Tool: %s' % relative

    # WorkflowTool
    def notifyCreated(self, ob):
        pass
