##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Role import gather_permissions
import Globals
from Acquisition import aq_get, aq_inner, aq_parent
from string import split

try: from OFS.ObjectManager import UNIQUE
except ImportError: UNIQUE = 2


# Tool for getting at Tools, meant to be modified as policies or Tool
# implementations change without having to affect the consumer.

_marker = []  # Create a new marker object.

def getPortal(ob):
    # This isn't as efficient as it could be.
    while ob is not None:
        if getattr(ob, '_isPortalRoot', 0):
            return ob
        ob = aq_parent(aq_inner(ob))

def getToolByName(obj, name, default=_marker):
    " Get the tool, 'toolname', by acquiring it. "
    try:
        tool = aq_get(obj, name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default
    else:
        if tool is _marker:
            raise AttributeError, name
        return tool


class ImmutableId (Base):
    def _setId(self, id):
        if id != self.id:
            raise Globals.MessageDialog(
                title='Invalid Id',
                message='Cannot change the id of this object',
                action ='./manage_main',)


class UniqueObject (ImmutableId):
    __replaceable__ = UNIQUE

    
def tuplize( valueName, value ):
    if type(value) == type(()): return value
    if type(value) == type([]): return tuple( value )
    if type(value) == type(''): return tuple( split( value ) )
    raise ValueError, "%s of unsupported type" % valueName

try:
    # Zope 2.2.x access control.
    from AccessControl import getSecurityManager
    def _getAuthenticatedUser(self):
        return getSecurityManager().getUser()
    def _checkPermission(permission, obj):
        return getSecurityManager().checkPermission(permission, obj)
except:
    # Zope 2.1.x access control.
    from AccessControl import User
    def _getAuthenticatedUser(self):
        u = self.REQUEST.get('AUTHENTICATED_USER', None)
        if u is None:
            u = User.nobody
        return u
    def _checkPermission(permission, obj):
        return _getAuthenticatedUser(obj).has_permission(permission, obj)


# If Zope ever provides a call to getRolesInContext() through
# the SecurityManager API, the method below needs to be updated.
def limitGrantedRoles(roles, context, special_roles=()):
    # Only allow a user to grant roles already possessed by that user,
    # with the exception that all special_roles can also be granted.
    user = _getAuthenticatedUser(context)
    if user is None:
        user_roles = ()
    else:
        user_roles = user.getRolesInContext(context)
    if 'Manager' in user_roles:
        # Assume all other roles are allowed.
        return
    for role in roles:
        if role not in special_roles and role not in user_roles:
            raise 'Unauthorized', 'Too many roles specified.'

def mergedLocalRoles(object):
    """Returns a merging of object and its ancestors'
    __ac_local_roles__."""
    # Modified from AccessControl.User.getRolesInContext().
    merged = {}
    object = getattr(object, 'aq_inner', object)
    while 1:
        if hasattr(object, '__ac_local_roles__'):
            dict = object.__ac_local_roles__ or {}
            if callable(dict): dict = dict()
            for k, v in dict.items():
                if merged.has_key(k):
                    merged[k] = merged[k] + v
                else:
                    merged[k] = v
        if hasattr(object, 'aq_parent'):
            object=object.aq_parent
            object=getattr(object, 'aq_inner', object)
            continue
        if hasattr(object, 'im_self'):
            object=object.im_self
            object=getattr(object, 'aq_inner', object)
            continue
        break
    return merged

def ac_inherited_permissions(ob, all=0):
    # Get all permissions not defined in ourself that are inherited
    # This will be a sequence of tuples with a name as the first item and
    # an empty tuple as the second.
    d = {}
    perms = getattr(ob, '__ac_permissions__', ())
    for p in perms: d[p[0]] = None
    r = gather_permissions(ob.__class__, [], d)
    if all:
       if hasattr(ob, '_subobject_permissions'):
           for p in ob._subobject_permissions():
               pname=p[0]
               if not d.has_key(pname):
                   d[pname]=1
                   r.append(p)
       r = list(perms) + r
    return r

def modifyPermissionMappings(ob, map):
    '''
    Modifies multiple role to permission mappings.
    '''
    # This mimics what AccessControl/Role.py does.
    # Needless to say, it's crude. :-(
    map = map.copy()  # Safety.
    for perm in ac_inherited_permissions(ob, 1):
        name, value = perm[:2]
        if map.has_key(name):
            for (role, allow) in map[name].items():
                p = Permission(name, value, ob)
                p.setRole(role, allow)  # Will only modify if it should.
            del map[name]
    if map:
        for name, (role, allow) in map.items():
            p = Permission(name, (), ob)
            p.setRole(role, allow)


from Globals import HTMLFile

addInstanceForm = HTMLFile('dtml/addInstance', globals())


class ToolInit:
    '''Utility class that can generate the factories for several tools
    at once.'''
    __name__ = 'toolinit'

    security = ClassSecurityInfo()
    security.declareObjectPrivate()     # equivalent of __roles__ = ()

    def __init__(self, meta_type, tools, product_name, icon):
        ''
        self.meta_type = meta_type
        self.tools = tools
        self.product_name = product_name
        self.icon = icon

    def initialize(self, context):
        # Add only one meta type to the folder add list.
        context.registerClass(
            meta_type = self.meta_type,
            # This is a little sneaky: we add self to the
            # FactoryDispatcher under the name "toolinit".
            # manage_addTool() can then grab it.
            constructors = (manage_addToolForm,
                            manage_addTool,
                            self,),
            icon = self.icon
            )

        for tool in self.tools:
            tool.__factory_meta_type__ = self.meta_type
            tool.icon = 'misc_/%s/%s' % (self.product_name, self.icon)


def manage_addToolForm(self, REQUEST):
    '''
    Shows the add tool form.
    '''
    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    tl = []
    for tool in toolinit.tools:
        tl.append(tool.meta_type)
    return addInstanceForm(addInstanceForm, self, REQUEST,
                           factory_action='manage_addTool',
                           factory_meta_type=toolinit.meta_type,
                           factory_product_name=toolinit.product_name,
                           factory_icon=toolinit.icon,
                           factory_types_list=tl,
                           factory_need_id=0)

def manage_addTool(self, type, REQUEST=None):
    '''Adds the tool specified by name.'''
    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    obj = None
    for tool in toolinit.tools:
        if tool.meta_type == type:
            obj = tool()
            break
    if obj is None:
        raise 'NotFound', type
    self._setObject(obj.id, obj)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


#
#   Now, do the same for creating content factories.
#
class ContentInit:
    """
        Utility class that can generate the factories for several
        content types at once.
    """
    __name__ = 'contentinit'

    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__( self
                , meta_type
                , content_types
                , permission=None
                , extra_constructors=()
                , fti=()
                ):
        ''
        self.meta_type = meta_type
        self.content_types = content_types
        self.permission = permission
        self.extra_constructors = extra_constructors
        self.fti = fti

    def initialize(self, context):
        # Add only one meta type to the folder add list.
        context.registerClass(
            meta_type = self.meta_type
            # This is a little sneaky: we add self to the
            # FactoryDispatcher under the name "contentinit".
            # manage_addContentType() can then grab it.
            , constructors = ( manage_addContentForm
                               , manage_addContent
                               , self
                               , ('factory_type_information', self.fti)
                               ) + self.extra_constructors
            , permission = self.permission
            )

        for ct in self.content_types:
            ct.__factory_meta_type__ = self.meta_type

def manage_addContentForm(self, REQUEST):
    '''
    Shows the add content type form.
    '''
    # self is a FactoryDispatcher.
    ci = self.contentinit
    tl = []
    for t in ci.content_types:
        tl.append(t.meta_type)
    return addInstanceForm(addInstanceForm, self, REQUEST,
                           factory_action='manage_addContent',
                           factory_meta_type=ci.meta_type,
                           factory_icon=None,
                           factory_types_list=tl,
                           factory_need_id=1)

def manage_addContent( self, id, type, REQUEST=None ):
    '''
        Adds the content type specified by name.
    '''
    # self is a FactoryDispatcher.
    contentinit = self.contentinit
    obj = None
    for content_type in contentinit.content_types:
        if content_type.meta_type == type:
            obj = content_type( id )
            break
    if obj is None:
        raise 'NotFound', type
    self._setObject( id, obj )
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)



from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

class SimpleItemWithProperties (PropertyManager, SimpleItem):
    '''
    A common base class for objects with configurable
    properties in a fixed schema.
    '''
    manage_options = (
        PropertyManager.manage_options
        + SimpleItem.manage_options)


    security = ClassSecurityInfo()
    security.declarePrivate(
        'manage_addProperty',
        'manage_delProperties',
        'manage_changePropertyTypes',
        )

    def manage_propertiesForm(self, REQUEST, *args, **kw):
        'An override that makes the schema fixed.'
        my_kw = kw.copy()
        my_kw['property_extensible_schema__'] = 0
        return apply(PropertyManager.manage_propertiesForm,
                     (self, self, REQUEST,) + args, my_kw)

    security.declarePublic('propertyLabel')
    def propertyLabel(self, id):
        """Return a label for the given property id
        """
        for p in self._properties:
            if p['id'] == id:
                return p.get('label', id)
        return id



import OFS
import sys
from os import path
from App.Common import package_home

def initializeBasesPhase1(base_classes, module):
    """
    Executes the first part of initialization of ZClass base classes.
    Stuffs a _ZClass_for_x class in the module for each base.
    """
    rval = []
    for base_class in base_classes:
        d={}
        zclass_name = '_ZClass_for_%s' % base_class.__name__
        exec 'class %s: pass' % zclass_name in d
        Z = d[ zclass_name ]
        Z.propertysheets = OFS.PropertySheets.PropertySheets()
        Z._zclass_ = base_class
        Z.manage_options = ()
        Z.__module__ = module.__name__
        setattr( module, zclass_name, Z )
        rval.append(Z)
    return rval

def initializeBasesPhase2(zclasses, context):
    """
    Finishes ZClass base initialization.  zclasses is the list returned
    by initializeBasesPhase1().  context is a ProductContext object.
    """
    for zclass in zclasses:
        context.registerZClass(zclass)

def registerIcon(klass, iconspec, _prefix=None):
    modname = klass.__module__
    pid = split(modname, '.')[1]
    name = path.split(iconspec)[1]
    klass.icon = 'misc_/%s/%s' % (pid, name)
    icon = Globals.ImageFile(iconspec, _prefix)
    icon.__roles__=None
    if not hasattr(OFS.misc_.misc_, pid):
        setattr(OFS.misc_.misc_, pid, OFS.misc_.Misc_(pid, {}))
    getattr(OFS.misc_.misc_, pid)[name]=icon


if 0:
    # Hopefully we can use this.

    from Globals import Persistent

    class NotifyOnModify (Persistent):
        '''
        This base class allows instances to be notified when there are
        changes that would affect persistence.
        '''

        __ready = 0

        def _setNotifyModified(self):
            self.__ready = 1

        def __doNotify(self):
            if self.__ready:
                dict = self.__dict__
                if not dict.has_key('__notified_on_modify__'):
                    dict['__notified_on_modify__'] = 1
                    self.notifyModified()

        def __setattr__(self, name, val):
            self.__dict__[name] = val
            self._p_changed = 1
            self.__doNotify()

        def __delattr__(self, name):
            del self.__dict__[name]
            self._p_changed = 1
            self.__doNotify()

        def notifyModified(self):
            # To be overridden.
            pass


if 0:
  # Prototype for a "UniqueId" base ZClass.
  import OFS

  class UniqueSheet(OFS.PropertySheets.PropertySheet,
                  OFS.PropertySheets.View):
    'Manage id of unique objects'

    manage = Globals.HTMLFile('uniqueid', globals())

    def getId(self):
        return self.getClassAttr('id')

    def manage_edit(self, id, REQUEST=None):
        self.setClassAttr('id', id)
        if REQUEST is not None:
            return self.manage(self, REQUEST)


  class ZUniqueObjectPropertySheets(OFS.PropertySheets.PropertySheets):

    unique = UniqueSheet('unique')

  class ZUniqueObject:
    '''Mix-in for unique zclass instances.'''

    _zclass_ = UniqueObject

    propertysheets = ZUniqueObjectPropertySheets()

    manage_options = (
        {'label': 'Id', 'action':'propertysheets/unique/manage'},
        )
