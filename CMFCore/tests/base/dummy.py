from Acquisition import Implicit, aq_inner, aq_parent
from OFS.SimpleItem import Item
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from security import OmnipotentUser


class DummyObject(Implicit):
    """
    A dummy callable object.
    Comes with getIcon and restrictedTraverse
    methods.
    """
    def __init__(self, id='dummy',**kw):
        self._id = id
        self.__dict__.update( kw )
        
    def __str__(self):
        return self._id
    
    def __call__(self):
        return self._id

    def restrictedTraverse( self, path ):
        return path and getattr( self, path ) or self

    def getIcon( self, relative=0 ):
        return 'Site: %s' % relative
    
    def getId(self):
        return self._id


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


class DummyFactory:
    """
    Dummy Product Factory
    """
    def __init__( self, folder ):
        self._folder = folder

    def getId(self):
        return 'DummyFactory'

    def addFoo( self, id, *args, **kw ):
        if getattr(self._folder, '_prefix', None):
            id = '%s_%s' % ( self._folder._prefix, id )
        foo = DummyContent(id, *args, **kw)
        self._folder._setObject(id, foo)
        if getattr(self._folder, '_prefix', None):
            return id

    __roles__ = ( 'FooAdder', )
    __allow_access_to_unprotected_subobjects__ = { 'addFoo' : 1 }


DummyFTI = FTI( 'Dummy Content'
              , title='Dummy Content Title'
              , meta_type=DummyContent.meta_type
              , product='FooProduct'
              , factory='addFoo'
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
    def __init__( self, id='dummy', fake_product=0, prefix='' ):
        self._prefix = prefix
        self._id = id

        if fake_product:
            self.manage_addProduct = { 'FooProduct' : DummyFactory( self ) }
    
    def _setOb(self, id, object):
        setattr(self, id, object)
        return self._getOb(id)

    def _getOb( self, id ):
        return getattr(self, id)

    _setObject = _setOb

    def getPhysicalPath(self):
        return self.aq_inner.aq_parent.getPhysicalPath() + ( self._id, )

    def getId(self):
        return self._id

    def reindexObjectSecurity(self):
        pass


class DummySite(DummyFolder):
    """ A dummy portal folder.
    """

    _domain = 'http://www.foobar.com'
    _path = 'bar'
    __ac_roles__ = ('Member', 'Reviewer')

    def absolute_url(self, relative=0):
        return '/'.join( (self._domain, self._path, self._id) )

    def getPhysicalPath(self):
        return ('', self._path, self._id)

    def getPhysicalRoot(self):
        return self

    def unrestrictedTraverse(self, path, default=None, restricted=0):
        return self.acl_users


class DummyUser(Implicit):
    """ A dummy User.
    """

    def __init__(self, id='dummy'):
        self.id = id

    def getId(self):
        return self.id

    getUserName = getId

    def allowed(self, object, object_roles=None):
        if object.getId() == 'portal_membership':
            return 0
        if object_roles:
            if 'FooAdder' in object_roles:
                return 0
        return 1

    def getRolesInContext(self, object):
        return ('Authenticated', 'Dummy', 'Member')


class DummyUserFolder(Implicit):
    """ A dummy User Folder with 2 dummy Users.
    """

    id = 'acl_users'

    def __init__(self):
        setattr( self, 'user_foo', DummyUser(id='user_foo') )
        setattr( self, 'user_bar', DummyUser(id='user_bar') )
        setattr( self, 'all_powerful_Oz', OmnipotentUser() )

    def getUsers(self):
        pass

    def getUser(self, name):
        return getattr(self, name, None)

    def getUserById(self, id, default=None):
        return self.getUser(id)

    def userFolderDelUsers(self, names):
        for user_id in names:
            delattr(self, user_id)


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
    test_notified = None

    def notifyCreated(self, ob):
        self.test_notified = ob


class DummyCachingManager:

    def getHTTPCachingHeaders( self, content, view_name, keywords, time=None ):
        return ( ( 'foo', 'Foo' ), ( 'bar', 'Bar' ) )

    def getPhysicalPath(self):
        return ('baz',)
