##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

"""
    Type registration tool.
    $Id$
"""
__version__='$Revision$'[11:-2]

import OFS
from Globals import InitializeClass, DTMLFile
from utils import UniqueObject, SimpleItemWithProperties, tuplize
from utils import _dtmldir, _checkPermission, cookString
import string
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_base
import Products, CMFCorePermissions

from CMFCorePermissions import View, ManagePortal, AccessContentsInformation

_marker = []  # Create a new marker.

class TypeInformation (SimpleItemWithProperties):
    """
    Base class for information about a content type.
    """
    _isTypeInformation = 1

    manage_options = (SimpleItemWithProperties.manage_options[:1] +
                      ({'label':'Actions',
                        'action':'manage_editActionsForm'},) +
                      SimpleItemWithProperties.manage_options[1:])


    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                              )


    _basic_properties = (
        {'id':'title', 'type': 'string', 'mode':'w',
         'label':'Title'},
        {'id':'description', 'type': 'text', 'mode':'w',
         'label':'Description'},
        {'id':'content_meta_type', 'type': 'string', 'mode':'w',
         'label':'Meta type'},
        {'id':'content_icon', 'type': 'string', 'mode':'w',
         'label':'Icon'},
        )

    _advanced_properties = (
        {'id':'immediate_view', 'type': 'string', 'mode':'w',
         'label':'Initial view name'},
        {'id':'filter_content_types', 'type': 'boolean', 'mode':'w',
         'label':'Filter content types?'},
        {'id':'allowed_content_types'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Allowed content types'
         , 'select_variable':'listContentTypes'
         },
        { 'id': 'allow_discussion', 'type': 'boolean', 'mode': 'w'
          , 'label': 'Allow Discussion?'
          },
        )

    title = ''
    description = ''
    content_meta_type = ''
    content_icon = ''
    immediate_view = ''
    filter_content_types = 1
    allowed_content_types = ()
    allow_discussion = 0
    _actions = ()

    def __init__(self, id, **kw):
        self.id = id
        if kw:
            kw = kw.copy()  # Get a modifiable dict.
            if (not kw.has_key('content_meta_type')
                and kw.has_key('meta_type')):
                kw['content_meta_type'] = kw['meta_type']
            if (not kw.has_key('content_icon')
                and kw.has_key('icon')):
                kw['content_icon'] = kw['icon']
            apply(self.manage_changeProperties, (), kw)
            if kw.has_key('actions'):
                aa = kw['actions']
                actions = []
                for action in aa:
                    action = action.copy()
                    # Some backward compatibility stuff.
                    if not action.has_key('id'):
                        action['id'] = cookString(action['name'])
                    if not action.has_key('category'):
                        action['category'] = 'object'
                    actions.append(action)
                self._actions = tuple(actions)

    #
    #   Accessors
    #
    security.declareProtected(View, 'Type')
    def Type(self):
        """
            Return the "human readable" type name (note that it
            may not map exactly to the 'meta_type', e.g., for
            l10n/i18n or where a single content class is being
            used twice, under different names.
        """
        if self.title:
            return self.title
        else:
            return self.getId()
    
    security.declareProtected(View, 'Description')
    def Description(self):
        """
            Textual description of the class of objects (intended
            for display in a "constructor list").
        """
        return self.description

    security.declareProtected(View, 'Metatype')
    def Metatype(self):
        """
            Returns the Zope 'meta_type' for this content object.
            May be used for building the list of portal content
            meta types.
        """
        return self.content_meta_type

    security.declareProtected(View, 'getIcon')
    def getIcon(self):
        """
            Returns the icon for this content object.
        """
        return self.content_icon

    security.declarePublic('allowType')
    def allowType( self, contentType ):
        """
            Can objects of 'contentType' be added to containers whose
            type object we are?
        """
        if not self.filter_content_types:
            return 1
        return contentType in self.allowed_content_types
    
    security.declarePublic('getId')
    def getId(self):
        return self.id

    security.declarePublic('allowDiscussion')
    def allowDiscussion( self ):
        """
            Can this type of object support discussion?
        """
        return self.allow_discussion

    security.declarePrivate('getActions')
    def getActions(self):
        """
        Returns the customizable user actions.
        """
        # Private because this returns the actual structure.
        return self._actions

    security.declarePublic('getActionById')
    def getActionById( self, id, default=_marker ):
        """
            Return the URL of the action whose ID is id.
        """
        for action in self.getActions():

            if action.has_key('id'):
                if action['id'] == id:
                    return action['action']
            else:
                # Temporary backward compatibility.
                if string.lower(action['name']) == id:
                    return action['action']

        if default is _marker:
            raise TypeError, ( 'No action "%s" for type "%s"'
                             % ( id, self.getId() )
                             )
        else:
            return default

    #
    #  Action editing interface
    #
    _actions_form = DTMLFile( 'editActions', _dtmldir )
    
    security.declareProtected(ManagePortal, 'manage_editActionsForm')
    def manage_editActionsForm(self, REQUEST, manage_tabs_message=None):
        """
        Shows the 'Actions' management tab.
        """
        actions = []
        for a in self.getActions():
            a = a.copy()
            p = a['permissions']
            if p:
                a['permission'] = p[0]
            else:
                a['permission'] = ''
            if not a.has_key('category'):
                a['category'] = 'object'
            if not a.has_key('id'):
                a['id'] = cookString(a['name'])
            if not a.has_key( 'visible' ):
                a['visible'] = 1
            actions.append(a)
        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form(self, REQUEST,
                                  actions=actions,
                                  possible_permissions=pp,
                                  management_view='Actions',
                                  manage_tabs_message=manage_tabs_message)

    security.declareProtected(ManagePortal, 'addAction')
    def addAction( self
                 , id
                 , name
                 , action
                 , permission
                 , category
                 , visible=1
                 , REQUEST=None
                 ):
        """
        Adds an action to the list.
        """
        if not name:
            raise ValueError('A name is required.')
        self._actions = self._actions + (
            {'id': str(id),
             'name': str(name),
             'action': str(action),
             'permissions': (str(permission),),
             'category': str(category),
             'visible': int(visible),
             },)
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')
    
    security.declareProtected(ManagePortal, 'changeActions')
    def changeActions(self, properties=None, REQUEST=None):
        """
        Changes the _actions.
        """
        if properties is None:
            properties = REQUEST
        actions = []
        for idx in range(len(self._actions)):
            s_idx = str(idx)
            action = {
                'id': str(properties.get('id_' + s_idx, '')),
                'name': str(properties.get('name_' + s_idx, '')),
                'action': str(properties.get('action_' + s_idx, '')),
                'permissions':
                (properties.get('permission_' + s_idx, ()),),
                'category': str(properties.get('category_' + s_idx, '')),
                'visible': not not properties.get('visible_' + s_idx, 0),
                }
            if not action['name']:
                raise ValueError('A name is required.')
            actions.append(action)
        self._actions = tuple(actions)
        if REQUEST is not None:
            return self.manage_editActionsForm(REQUEST, manage_tabs_message=
                                               'Actions changed.')

    security.declareProtected(ManagePortal, 'deleteActions')
    def deleteActions(self, selections=(), REQUEST=None):
        """
        Deletes actions.
        """
        actions = list(self._actions)
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        sels.reverse()
        for idx in sels:
            del actions[idx]
        self._actions = tuple(actions)
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Deleted %d action(s).' % len(sels)))

    security.declareProtected(ManagePortal, 'moveUpActions')
    def moveUpActions(self, selections=(), REQUEST=None):
        """
        Moves the specified actions up one slot.
        """
        actions = list(self._actions)
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        for idx in sels:
            idx2 = idx - 1
            if idx2 < 0:
                # Wrap to the bottom.
                idx2 = len(actions) - 1
            # Swap.
            a = actions[idx2]
            actions[idx2] = actions[idx]
            actions[idx] = a
        self._actions = tuple(actions)
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved up %d action(s).' % len(sels)))

    security.declareProtected(ManagePortal, 'moveDownActions')
    def moveDownActions(self, selections=(), REQUEST=None):
        """
        Moves the specified actions down one slot.
        """
        actions = list(self._actions)
        sels = list(map(int, selections))  # Convert to a list of integers.
        sels.sort()
        sels.reverse()
        for idx in sels:
            idx2 = idx + 1
            if idx2 >= len(actions):
                # Wrap to the top.
                idx2 = 0
            # Swap.
            a = actions[idx2]
            actions[idx2] = actions[idx]
            actions[idx] = a
        self._actions = tuple(actions)
        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message=(
                'Moved down %d action(s).' % len(sels)))

InitializeClass( TypeInformation )


class FactoryTypeInformation (TypeInformation):
    """
    Portal content factory.
    """
    meta_type = 'Factory-based Type Information'
    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'product', 'type': 'string', 'mode':'w',
         'label':'Product name'},
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Factory method in product'},
        ) + TypeInformation._advanced_properties)

    product = ''
    factory = ''
 
    #
    #   Agent methods
    #
    def _getFactoryMethod(self, container, raise_exc=0):
        if not self.product or not self.factory:
            return None
        try:
            p = container.manage_addProduct[self.product]
            m = getattr(p, self.factory, None)
            if m is not None:
                if getSecurityManager().validate(p, p, self.factory, m):
                    return m
            return None
        except: # only raise if allowed
            if raise_exc:
                raise
            return None

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed ( self, container, raise_exc=0):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        m = self._getFactoryMethod(container, raise_exc)
        return (m is not None)

    security.declarePublic('constructInstance')
    def constructInstance( self, container, id, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.  Return the URL
        of its "immediate" view (typically the metadata form).
        """
        # Get the factory method, performing a security check
        # in the process.
        m = self._getFactoryMethod(container, raise_exc=1)

        if m is None:
            raise 'Unauthorized', ('Cannot create %s' % self.getId())

        id = str(id)

        if getattr( m, 'isDocTemp', 0 ):
            args = ( m.aq_parent, self.REQUEST ) + args
            kw[ 'id' ] = id
        else:
            args = ( id, ) + args

        id = apply( m, args, kw ) or id  # allow factory to munge ID
        ob = container._getOb( id )

        if hasattr(ob, '_setPortalTypeName'):
            ob._setPortalTypeName(self.getId())

        return ob

InitializeClass( FactoryTypeInformation )


class ScriptableTypeInformation( TypeInformation ):
    """
    Invokes a script rather than a factory to create the content.
    """
    meta_type = 'Scriptable Type Information'
    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'permission', 'type': 'string', 'mode':'w',
         'label':'Constructor permission'},
        {'id':'constructor_path', 'type': 'string', 'mode':'w',
         'label':'Constructor path'},
        ) + TypeInformation._advanced_properties)

    permission = ''
    constructor_path = ''

    #
    #   Agent methods
    #
    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        permission = self.permission
        if permission and not _checkPermission( permission, container ):
            return 0
        return 1

    security.declarePublic('constructInstance')
    def constructInstance( self, container, id, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.  Return the URL
        of its "immediate" view (typically the metadata form).
        """
        if not self.isConstructionAllowed(container):
            raise 'Unauthorized'

        constructor = self.restrictedTraverse( self.constructor_path )
        #   Rewrap to get into container's context.
        constructor = aq_base(constructor).__of__( container )

        id = str(id)
        ob = apply(constructor, (container, id) + args, kw)
        if hasattr(ob, '_setPortalTypeName'):
            ob._setPortalTypeName(self.getId())

        return ob

InitializeClass( ScriptableTypeInformation )


# Provide aliases for backward compatibility.
ContentFactoryMetadata = FactoryTypeInformation
ContentTypeInformation = ScriptableTypeInformation


allowedTypes = ( 'Script (Python)'
               , 'Python Method'
               , 'DTML Method'
               , 'External Method'
               , FactoryTypeInformation.meta_type
               , ScriptableTypeInformation.meta_type
               )

class TypesTool( UniqueObject, OFS.Folder.Folder ):
    """
        Provides a configurable registry of portal content types.
    """
    id = 'portal_types'
    meta_type = 'CMF Types Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + OFS.Folder.Folder.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainTypesTool', _dtmldir )

    def all_meta_types(self):
        all = TypesTool.inheritedAttribute('all_meta_types')(self)
        return (
            {'name':FactoryTypeInformation.meta_type,
             'action':'manage_addFactoryTIForm',
             'permission':'Manage portal'},
            {'name':ScriptableTypeInformation.meta_type,
             'action':'manage_addScriptableTIForm',
             'permission':'Manage portal'},
            ) + tuple(all)

    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = TypesTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in allowedTypes:
                meta_types.append(meta_type)
        return meta_types

    security.declareProtected(ManagePortal, 'listDefaultTypeInformation')
    def listDefaultTypeInformation(self):
        # Scans for factory_type_information attributes
        # of all products and factory dispatchers within products.
        res = []
        products = self.aq_acquire('_getProducts')()
        for product in products.objectValues():
            if hasattr(aq_base(product), 'factory_type_information'):
                ftis = product.factory_type_information
            else:
                package = getattr(Products, product.getId(), None)
                dispatcher = getattr(package, '__FactoryDispatcher__', None)
                ftis = getattr(dispatcher, 'factory_type_information', None)
            if ftis is not None:
                if callable(ftis):
                    ftis = ftis()
                for fti in ftis:
                    mt = fti.get('meta_type', None)
                    if mt:
                        res.append((product.getId() + ': ' + mt, fti))
        return res

    _addTIForm = DTMLFile( 'addTypeInfo', _dtmldir )

    security.declareProtected(ManagePortal, 'manage_addFactoryTIForm')
    def manage_addFactoryTIForm(self, REQUEST):
        ' '
        return self._addTIForm(self, REQUEST, scriptable='',
                               types=self.listDefaultTypeInformation())

    security.declareProtected(ManagePortal, 'manage_addScriptableTIForm')
    def manage_addScriptableTIForm(self, REQUEST):
        ' '
        return self._addTIForm(self, REQUEST, scriptable='1',
                               types=self.listDefaultTypeInformation())

    security.declareProtected(ManagePortal, 'manage_addTypeInformation')
    def manage_addTypeInformation(self, id=None, scriptable='',
                                  typeinfo_name=None, RESPONSE=None):
        """
        Create a TypeInformation in self.
        """
        fti = None
        if typeinfo_name:
            info = self.listDefaultTypeInformation()
            for (name, ft) in info:
                if name == typeinfo_name:
                    fti = ft
                    break
            if fti is None:
                raise 'Bad Request', ('%s not found.' % typeinfo_name)
            if not id:
                id = fti.get('id', None)
        if not id:
            raise 'Bad Request', 'An id is required.'
        if scriptable:
            klass = ScriptableTypeInformation
        else:
            klass = FactoryTypeInformation
        id = str(id)
        if fti is not None:
            fti = fti.copy()
            if fti.has_key('id'):
                del fti['id']
            ob = apply(klass, (id,), fti)
        else:
            ob = apply(klass, (id,))
        self._setObject(id, ob)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_main' % self.absolute_url())

    security.declareProtected(AccessContentsInformation, 'getTypeInfo')
    def getTypeInfo( self, contentType ):
        """
            Return an instance which implements the
            TypeInformation interface, corresponding to
            the specified 'contentType'.  If contentType is actually
            an object, rather than a string, attempt to look up
            the appropriate type info using its Type or meta_type.
        """
        if type( contentType ) is not type( '' ):
            try:
                contentType = contentType._getPortalTypeName()
            except: # if we can't get or call it for any reason, fall back...
                contentType = contentType.meta_type
        ob = getattr( self, contentType, None )
        if getattr(aq_base(ob), '_isTypeInformation', 0):
            return ob
        else:
            return None

    security.declareProtected(AccessContentsInformation, 'listTypeInfo')
    def listTypeInfo( self, container=None ):
        """
            Return a sequence of instances which implement the
            TypeInformation interface, one for each content
            type registered in the portal.
        """
        rval = []
        for t in self.objectValues():
            # Filter out things that aren't TypeInformation and
            # types for which the user does not have adequate permission.
            if not getattr(aq_base(t), '_isTypeInformation', 0):
                continue
            if not t.Type():
                # Not ready.
                continue
            if container is not None:
                if not t.isConstructionAllowed(container):
                    continue
            rval.append(t)
        return rval

    security.declareProtected(AccessContentsInformation, 'listContentTypes')
    def listContentTypes( self, container=None, by_metatype=0 ):
        """
            Return list of content metatypes.
        """
        typenames = {}
        for t in self.listTypeInfo( container ):

            if by_metatype:
                name = t.Metatype()
            else:
                name = t.Type()

            if name:
                typenames[ name ] = 1

        result = typenames.keys()
        result.sort()
        return result

    
    security.declarePublic('constructContent')
    def constructContent( self
                        , type_name
                        , container
                        , id
                        , RESPONSE=None
                        , *args
                        , **kw
                        ):
        """
            Build an instance of the appropriate content class in
            'container', using 'id'.
        """
        info = self.getTypeInfo( type_name )
        if info is None:
            raise 'ValueError', 'No such content type: %s' % type_name
        
        ob = apply(info.constructInstance, (container, id) + args, kw)

        ob.reindexObject()

        if RESPONSE is not None:
            immediate_url = '%s/%s' % ( ob.absolute_url()
                                      , info.immediate_view )
            RESPONSE.redirect( immediate_url )

InitializeClass( TypesTool )
