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

from types import StringType

from ExtensionClass import Base
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permission import Permission
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Role import gather_permissions
import Globals
from Acquisition import aq_get, aq_inner, aq_parent
from string import split
import os, re
from Globals import package_home

try: from OFS.ObjectManager import UNIQUE
except ImportError: UNIQUE = 2


_dtmldir = os.path.join( package_home( globals() ), 'dtml' )


# Tool for getting at Tools, meant to be modified as policies or Tool
# implementations change without having to affect the consumer.

_marker = []  # Create a new marker object.

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
        if id != self.getId():
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

def _getAuthenticatedUser( self ):
    return getSecurityManager().getUser()

def _checkPermission(permission, obj, StringType = type('')):
    roles = rolesForPermissionOn(permission, obj)
    if type(roles) is StringType:
        roles=[roles]
    if _getAuthenticatedUser( obj ).allowed( obj, roles ):
        return 1
    return 0


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
    something_changed = 0
    perm_info = ac_inherited_permissions(ob, 1)
    for name, settings in map.items():
        cur_roles = rolesForPermissionOn(name, ob)
        t = type(cur_roles)
        if t is StringType:
            cur_roles = [cur_roles]
        else:
            cur_roles = list(cur_roles)
        changed = 0
        for (role, allow) in settings.items():
            if not allow:
                if role in cur_roles:
                    changed = 1
                    cur_roles.remove(role)
            else:
                if role not in cur_roles:
                    changed = 1
                    cur_roles.append(role)
        if changed:
            data = ()  # The list of methods using this permission.
            for perm in perm_info:
                n, d = perm[:2]
                if n == name:
                    data = d
                    break
            p = Permission(name, data, ob)
            p.setRoles(tuple(cur_roles))
            something_changed = 1
    return something_changed


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
    self._setObject(obj.getId(), obj)
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

#
#   StructuredText handling.
#
import StructuredText
from StructuredText.HTMLWithImages import HTMLWithImages

_STXDWI = StructuredText.DocumentWithImages.__class__

class CMFDocumentClass( StructuredText.DocumentWithImages.__class__ ):
    """
    Override DWI to get '_' into links, and also turn on inner/named links.
    """
    text_types = [
        'doc_named_link',
        'doc_inner_link',
        ] + _STXDWI.text_types
    
    _URL_AND_PUNC = r'([a-zA-Z0-9_\@\.\,\?\!\/\:\;\-\#\~]+)'
    def doc_href( self
                , s
                , expr1 = re.compile( _STXDWI._DQUOTEDTEXT
                                    + "(:)"
                                    + _URL_AND_PUNC
                                    + _STXDWI._SPACES
                                    ).search
                , expr2 = re.compile( _STXDWI._DQUOTEDTEXT
                                    + r'(\,\s+)'
                                    + _URL_AND_PUNC
                                    + _STXDWI._SPACES
                                    ).search
                ):
        return _STXDWI.doc_href( self, s, expr1, expr2 )

CMFDocumentClass = CMFDocumentClass()

class CMFHtmlWithImages( HTMLWithImages ):
    """ Special subclass of HTMLWithImages, overriding document() """
    def namedLink(self, doc, level, output):
        """\
        XXX Trial subclassed implementation of HTMLClass#namedLink(),
        as default implementation seems to be broken...
        """
        name = doc.getNodeValue()
        if name[:2] == '..':
            name = name[2:]
        output('<a name="#%s">[%s]</a>' % (name, name))

    def document(self, doc, level, output):
        """\
        HTMLWithImages.document renders full HTML (head, title, body).  For
        CMF Purposes, we don't want that.  We just want those nice juicy
        body parts perfectly rendered.
        """
        for c in doc.getChildNodes():
           getattr(self, self.element_types[c.getNodeName()])(c, level, output)

CMFHtmlWithImages = CMFHtmlWithImages()
            
def _format_stx( text, level=1 ):
    """
        Render STX to HTML.
    """
    st = StructuredText.Basic( text )   # Creates the basic DOM
    if not st:                          # If it's an empty object
        return ""                       # return now or have errors!

    doc = CMFDocumentClass( st )
    html = CMFHtmlWithImages( doc, level )
    return html

### Metadata Keyword splitter utilities
import re, string, operator
KEYSPLITRE = re.compile(r'[,;]')
def keywordsplitter(headers,
                    names=('Subject', 'Keywords',),
                    splitter=KEYSPLITRE.split):
    """ Splits keywords out of headers, keyed on names.  Returns list. """
    out = []
    for head in names:
        keylist = splitter(headers.get(head, ''))
        keylist = map(string.strip, keylist)
        out.extend(filter(operator.truth, keylist))
    return out

#
#   Directory-handling utilities
#
def normalize(p):
    return path.abspath(path.normcase(p))

normINSTANCE_HOME = normalize(INSTANCE_HOME)
normSOFTWARE_HOME = normalize(SOFTWARE_HOME)

separators = (os.sep, os.altsep)

def expandpath(p):
    # Converts a minimal path to an absolute path.
    if path.isabs(p):
        return p
    abs = path.join(normINSTANCE_HOME, p)
    if path.exists(abs):
        return abs
    return path.join(normSOFTWARE_HOME, p)

def minimalpath(p):
    # Trims INSTANCE_HOME or SOFTWARE_HOME from a path.
    p = path.abspath(p)
    abs = normalize(p)
    l = len(normINSTANCE_HOME)
    if abs[:l] != normINSTANCE_HOME:
        l = len(normSOFTWARE_HOME)
        if abs[:l] != normSOFTWARE_HOME:
            # Can't minimize.
            return p
    p = p[l:]
    while p[:1] in separators:
        p = p[1:]
    return p

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
