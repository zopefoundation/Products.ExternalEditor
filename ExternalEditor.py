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

# Zope External Editor Product by Casey Duncan

import Acquisition
from AccessControl.SecurityManagement import getSecurityManager
import base64

class ExternalEditor(Acquisition.Implicit):
    """Create a response that encapsulates the data needed by the
       ZopeEdit help application
    """
    
    def __before_publishing_traverse__(self, self2, request):
        path = request['TraversalRequestNameStack']
        target = path[-1]
        request.set('target', target)
        path[:] = []
    
    def index_html(self, REQUEST, RESPONSE):
        """Publish the object to the external editor helper app"""
        
        security = getSecurityManager()
        ob = getattr(self.aq_parent, REQUEST['target'])
        
        if not security.checkPermission('View management screen', ob):
            raise 'Unauthorized'
        
        r = []
        r.append('url:%s' % ob.absolute_url())
        r.append('meta_type:%s' % ob.meta_type)
        
        if hasattr(ob, 'content_type'):
            r.append('content_type:%s' % ob.content_type)
           
        r.append('auth:%s' % REQUEST._auth)
        r.append('cookie:%s' % REQUEST.environ.get('HTTP_COOKIE',''))            
        r.append('')
        
        if hasattr(ob, 'document_src'):
            r.append(ob.document_src(REQUEST, RESPONSE))
        elif hasattr(ob, 'manage_FTPget'):
            r.append(ob.manage_FTPget(REQUEST, RESPONSE))
        elif hasattr(ob, 'EditableBody'):
            r.append(ob.EditableBody())
        elif hasattr(ob, 'read'):
            r.append(ob.read())
        else:
            # can't read it!
            raise 'BadRequest', 'Object does not support external editing'
        
        RESPONSE.setHeader('Content-Type', 'application/x-zope-edit')
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
            
        return '\n'.join(r)
        
        
