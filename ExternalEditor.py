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
import Acquisition
from AccessControl.SecurityManagement import getSecurityManager
from webdav.common import rfc1123_date

class ExternalEditor(Acquisition.Implicit):
    """Create a response that encapsulates the data needed by the
       ZopeEdit helper application
    """
    
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
            ob = parent[REQUEST['target']]
        except AttributeError:
            # Handle objects that are methods in ZClasses
            ob = parent.propertysheets.methods[REQUEST['target']]
        
        if not security.checkPermission('View management screen', ob):
            raise 'Unauthorized'
        
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
        r.append('')
        
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
        RESPONSE.setHeader('Pragma', 'no-cache')
            
        return join(r, '\n')
