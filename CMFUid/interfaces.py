##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Unique Id Generation and Handling

These interfaces are intentionaly kept close to those from Zope3. Additionaly
handling (IUniqueIdHandler) and generation (IUniqueIdGenerator) of unique ids 
are kept separate.

$Id$
"""

from Interface import Interface, Attribute

from Products.CMFCore.interfaces.IOpaqueItems \
    import ICallableOpaqueItem, ICallableOpaqueItemEvents

class UniqueIdError(Exception): pass


class IUniqueIdQuery(Interface):
    """Querying unique ids.
    """
    def queryUid(obj, default=None):
        """Return the unique id of the object.
        
        If the object doesn't have a unique, the default value is returned.
        """
        
    def getUid(obj):
        """Return the unique id of the object.
        
        If the object doesn't have a unique, a UniqueIdError is raised.
        """
        
    def queryObject(uid, default=None):
        """Return the object with the given uid.
        
        If no object exist with the given unique id, the default value is 
        returned.
        """
        
    def getObject(uid):
        """Return the object with the given uid.
        
        If no object exist with the given unique id, a UniqueIdError is raised.
        """


class IUniqueIdBrainQuery(Interface):
    """Querying unique ids returning brains for efficiency sake.
    """
    
    def queryBrain(uid, default=None):
        """Return the object with the given uid.
        
        If no object exist with the given unique id, the default value is 
        returned.
        
        Returning a brain is more efficient than returning the object.
        A brain usually exposes only parts of the object and should only 
        be read from. 
        
        If the implementing class doesn't support returning a catalog 
        brain it may fallback to return the object.
        """
        
    def getBrain(uid):
        """Return a brain of the object with the given uid.
        
        If no object exist with the given unique id, a UniqueIdError is raised.
        
        Returning a brain is more efficient than returning the object.
        A brain usually exposes only parts of the object and should only 
        be read from. 
        
        If the implementing class doesn't support returning a catalog 
        brain it may fallback to return the object.
        """


class IUniqueIdSet(Interface):
    """(Un)register unique ids on objects.
    """

    def register(obj):
        """Register the object and return the unique id generated for it.
        
        If the object is already registered, its unique id is returned 
        anyway.
        """

    def unregister(obj):
        """Remove the object from the indexes.
        
        UniqueIdError is raised if object was not registered previously.
        """

# Main API for plaing with unique ids
class IUniqueIdHandler(IUniqueIdSet, IUniqueIdQuery, IUniqueIdBrainQuery):
    """Handle registering, querying unique ids and objects.
    """


class IUniqueIdGenerator(Interface):
    """Generate a unique id.
    """
    
    def __call__():
        """Return a unique id value.
        """


class IUniqueIdAnnotation(ICallableOpaqueItem, ICallableOpaqueItemEvents):
    """Opaque unique id item handling adding, copying, and deletion events.
    """
    
    def setUid(uid):
        """Set the uid value the unique id annotation shall return.
        """


class IUniqueIdAnnotationManagement(Interface):
    """Manage unique id annotations.
    """
    
    def __call__(obj, id):
        """Attach an unique id attribute of 'id' to the passed object.
        
        Return a unique id object implementing 'IUniqueIdAnnotation'.
        """
