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
import types
import re
import urllib
import Acquisition
from Globals import InitializeClass
from App.Common import rfc1123_date
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS import Image
try:
    from webdav.Lockable import wl_isLocked
except ImportError:
    # webdav module not available
    def wl_isLocked(ob):
        return 0
try:
    from ZPublisher.Iterators import IStreamIterator
except ImportError:
    # pre-2.7.1 Zope without stream iterators
    IStreamIterator = None
    
ExternalEditorPermission = 'Use external editor'

class ExternalEditor(Acquisition.Implicit):
    """Create a response that encapsulates the data needed by the
       ZopeEdit helper application
    """
    
    security = ClassSecurityInfo()
    security.declareObjectProtected(ExternalEditorPermission)
    
    def __before_publishing_traverse__(self, self2, request):
        path = request['TraversalRequestNameStack']
        if path:
            target = path[-1]
            if request.get('macosx') and target.endswith('.zem'):
                # Remove extension added by EditLink() for Mac finder
                # so we can traverse to the target in Zope
                target = target[:-4]
            request.set('target', target)
            path[:] = []
        else:
            request.set('target', None)
    
    def index_html(self, REQUEST, RESPONSE, path=None):
        """Publish the object to the external editor helper app"""
        
        security = getSecurityManager()
        if path is None:
            parent = self.aq_parent
            try:
                ob = parent[REQUEST['target']] # Try getitem
            except KeyError:
                ob = getattr(parent, REQUEST['target']) # Try getattr
            except AttributeError:
                # Handle objects that are methods in ZClasses
                ob = parent.propertysheets.methods[REQUEST['target']]
        else:
            ob = self.restrictedTraverse( path )
        
        r = []
        r.append('url:%s' % ob.absolute_url())
        r.append('meta_type:%s' % ob.meta_type)
        
        title = getattr(Acquisition.aq_base(ob), 'title', None)
        if title is not None:
            if callable(title):
                title = title()
            r.append('title:%s' % title)
                
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
                    if REQUEST.get('borrow_lock'):
                        r.append('borrow_lock:1')
                    break       
              
        r.append('')
        streamiterator = None
        
        # Using RESPONSE.setHeader('Pragma', 'no-cache') would be better, but
        # this chokes crappy most MSIE versions when downloads happen on SSL.
        # cf. http://support.microsoft.com/support/kb/articles/q316/4/31.asp
        RESPONSE.setHeader('Last-Modified', rfc1123_date())
        
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
                body = ob.manage_FTPget()
            except TypeError: # some need the R/R pair!
                body = ob.manage_FTPget(REQUEST, RESPONSE)
        elif hasattr(ob, 'EditableBody'):
            body = ob.EditableBody()
        elif hasattr(ob, 'document_src'):
            body = ob.document_src(REQUEST, RESPONSE)
        elif hasattr(ob, 'read'):
            body = ob.read()
        else:
            # can't read it!
            raise 'BadRequest', 'Object does not support external editing'
        
        RESPONSE.setHeader('Content-Type', 'application/x-zope-edit')

        if (IStreamIterator is not None and
            IStreamIterator.isImplementedBy(body)):
            # We need to manage our content-length because we're streaming.
            # The content-length should have been set in the response by
            # the method that returns the iterator, but we need to fix it up
            # here because we insert metadata before the body.
            clen = RESPONSE.headers.get('content-length', None)
            assert clen is not None
            metadata = join(r, '\n')
            RESPONSE.setHeader('Content-Length', len(metadata) + int(clen) + 1)
            RESPONSE.write(metadata)
            RESPONSE.write('\n')
            for data in body:
                RESPONSE.write(data)
        else:
            r.append(body)
            return join(r, '\n')

InitializeClass(ExternalEditor)

is_mac_user_agent = re.compile('.*Mac OS X.*|.*Mac_PowerPC.*').match

def EditLink(self, object, borrow_lock=0):
    """Insert the external editor link to an object if appropriate"""
    base = Acquisition.aq_base(object)
    user = getSecurityManager().getUser()
    editable = (hasattr(base, 'manage_FTPget')
                or hasattr(base, 'EditableBody')
                or hasattr(base, 'document_src')
                or hasattr(base, 'read'))
    if editable and user.has_permission(ExternalEditorPermission, object):
        query = {}
        if is_mac_user_agent(object.REQUEST['HTTP_USER_AGENT']):
            # Add extension to URL so that the Mac finder can
            # launch the ZopeEditManager helper app
            # this is a workaround for limited MIME type
            # support on MacOS X browsers
            ext = '.zem'
            query['macosx'] = 1
        else:
            ext = ''
        if borrow_lock:
            query['borrow_lock'] = 1
        url = "%s/externalEdit_/%s%s%s" % (object.aq_parent.absolute_url(), 
                                           urllib.quote(object.getId()), 
                                           ext, querystr(query))
        return ('<a href="%s" '
                'title="Edit using external editor">'
                '<img src="%s/misc_/ExternalEditor/edit_icon" '
                'align="middle" hspace="2" border="0" alt="External Editor" />'
                '</a>' % (url, object.REQUEST.BASEPATH1)
               )
    else:
        return ''

def querystr(d):
    """Create a query string from a dict"""
    if d:
        return '?' + '&'.join(
            ['%s=%s' % (name, val) for name, val in d.items()])
    else:
        return ''

