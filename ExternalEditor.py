##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""$Id$
"""

# Zope External Editor Product by Casey Duncan

from string import join # For Zope 2.3 compatibility
import urllib
import Acquisition
from Globals import InitializeClass
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS import Image
try:
    from webdav.Lockable import wl_isLocked
except ImportError:
    # webdav module not available
    def wl_isLocked(ob):
        return 0

ExternalEditorPermission = 'Use external editor'

class ExternalEditor(Acquisition.Implicit):
    """Create a response that encapsulates the data needed by the
       ZopeEdit helper application
    """
    
    security = ClassSecurityInfo()
    security.declareObjectProtected(ExternalEditorPermission)
    
    def __before_publishing_traverse__(self, self2, request):
        path = request['TraversalRequestNameStack']
        target = path[-1]
        request.set('target', target)
        path[:] = []
    
    def index_html(self, REQUEST, RESPONSE):
        """Publish the object to the external editor helper app"""
        
        security = getSecurityManager()
        parent = self.aq_parent
        try:
            ob = parent[REQUEST['target']] # Try getitem
        except KeyError:
            ob = getattr(parent, REQUEST['target']) # Try getattr
        except AttributeError:
            # Handle objects that are methods in ZClasses
            ob = parent.propertysheets.methods[REQUEST['target']]
        
        r = []
        r.append('url:%s' % ob.absolute_url())
        r.append('meta_type:%s' % ob.meta_type)
        
        if hasattr(Acquisition.aq_base(ob), 'content_type'):
            if callable(ob.content_type):
                r.append('content_type:%s' % ob.content_type())
            else:
                r.append('content_type:%s' % ob.content_type)
                
        if REQUEST._auth:
            if REQUEST._auth[-1] == '\n':
                auth = REQUEST._auth[:-1]
            else:
                auth = REQUEST._auth
                
            r.append('auth:%s' % auth)
            
        r.append('cookie:%s' % REQUEST.environ.get('HTTP_COOKIE',''))
        
        if wl_isLocked(ob):
            # Object is locked, send down the lock token 
            # owned by this user (if any)
            user_id = security.getUser().getId()
            for lock in ob.wl_lockValues():
                if not lock.isValid():
                    continue # Skip invalid/expired locks
                creator = lock.getCreator()
                if creator and creator[1] == user_id:
                    # Found a lock for this user, so send it
                    r.append('lock-token:%s' % lock.getLockToken())
                    break       
              
        r.append('')
        
        RESPONSE.setHeader('Pragma', 'no-cache')
        
        if hasattr(Acquisition.aq_base(ob), 'data') \
           and hasattr(ob.data, '__class__') \
           and ob.data.__class__ is Image.Pdata:
            # We have a File instance with chunked data, lets stream it
            metadata = join(r, '\n')
            RESPONSE.setHeader('Content-Type', 'application/x-zope-edit')
            RESPONSE.setHeader('Content-Length', 
                               len(metadata) + ob.get_size() + 1)
            RESPONSE.write(metadata)
            RESPONSE.write('\n')
            data = ob.data
            while data is not None:
                RESPONSE.write(data.data)
                data = data.next         
            return ''
        if hasattr(ob, 'manage_FTPget'):
            try:
                r.append(ob.manage_FTPget())
            except TypeError: # some need the R/R pair!
                r.append(ob.manage_FTPget(REQUEST, RESPONSE))
        elif hasattr(ob, 'EditableBody'):
            r.append(ob.EditableBody())
        elif hasattr(ob, 'document_src'):
            r.append(ob.document_src(REQUEST, RESPONSE))
        elif hasattr(ob, 'read'):
            r.append(ob.read())
        else:
            # can't read it!
            raise 'BadRequest', 'Object does not support external editing'
        
        RESPONSE.setHeader('Content-Type', 'application/x-zope-edit')    
        return join(r, '\n')

InitializeClass(ExternalEditor)

def EditLink(self, object):
    """Insert the external editor link to an object if appropriate"""
    base = Acquisition.aq_base(object)
    user = getSecurityManager().getUser()
    editable = (hasattr(base, 'manage_FTPget')
                or hasattr(base, 'EditableBody')
                or hasattr(base, 'document_src')
                or hasattr(base, 'read'))
    if editable and user.has_permission(ExternalEditorPermission, object):
        return ('<a href="%s/externalEdit_/%s" '
                'title="Edit using external editor">'
                '<img src="%s/misc_/ExternalEditor/edit_icon" '
                'align="middle" hspace="2" border="0" alt="External Editor" />'
                '</a>' % (object.aq_parent.absolute_url(), 
                          urllib.quote(object.getId()),
                          object.REQUEST.BASEPATH1)
               )
    else:
        return ''
                
