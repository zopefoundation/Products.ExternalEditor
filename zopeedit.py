#!/usr/bin/env python
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

# Zope External Editor Helper Application by Casey Duncan

__version__ = '0.3'

import sys, os
from os import path
from tempfile import mktemp
from ConfigParser import ConfigParser
from httplib import HTTPConnection, HTTPSConnection
from urlparse import urlparse
import urllib

win32 = sys.platform == 'win32'

class Configuration:
    
    def __init__(self, path):
        # Create/read config file on instantiation
        self.path = path
        if not os.path.exists(path):
            f = open(path, 'w')
            f.write(default_configuration)
            f.close()
        self.changed = 0
        self.config = ConfigParser()
        self.config.readfp(open(path))
            
    def save(self):
        """Save config options to disk"""
        self.config.write(open(self.path, 'w'))
        self.changed = 0
            
    def set(self, section, option, value):
        self.config.set(section, option, value)
        self.changed = 1
    
    def __getattr__(self, name):
        # Delegate to the ConfigParser instance
        return getattr(self.config, name)
        
    def getAllOptions(self, meta_type, content_type, host_domain):
        """Return a dict of all applicable options for the
           given meta_type, content_type and host_domain
        """
        opt = {}
        sep = content_type.find('/')
        general_type = '%s/*' % content_type[:sep]
        
        # Divide up the domains segments and create a
        # list of domains from the bottom up
        host_domain = host_domain.split('.')
        domains = []
        for i in range(len(host_domain)):
            domains.append('domain:%s' % '.'.join(host_domain[i:]))
        domains.reverse()
        
        sections = ('general', 
                    'meta-type:%s' % meta_type,
                    'content-type:%s' % general_type,
                    'content-type:%s' % content_type,
                   ) + tuple(domains)
                   
        for section in sections:
            if self.config.has_section(section):
                for option in self.config.options(section):
                    opt[option] = self.config.get(section, option)
        return opt
        
class ExternalEditor:
    
    saved = 1
    
    def __init__(self, input_file):
        try:
            # Read the configuration file
            if win32:
                config_path = path.expanduser('~\ZopeExternalEdit.ini')
            else:
                config_path = path.expanduser('~/.zope-external-edit')
                
            self.config = Configuration(config_path)

            # Open the input file and read the metadata headers
            in_f = open(input_file)
            metadata = {}

            while 1:
                line = in_f.readline()[:-1]
                if not line: break
                sep = line.find(':')
                key = line[:sep]
                val = line[sep+1:]
                metadata[key] = val
            self.metadata = metadata
                               
            # parse the incoming url
            scheme, self.host, self.path = urlparse(metadata['url'])[:3]
            self.ssl = scheme == 'https'
            
            # Get all configuration options
            self.options = self.config.getAllOptions(
                                            metadata['meta_type'],
                                            metadata.get('content_type',''),
                                            self.host)

            # Write the body of the input file to a separate file
            content_file = urllib.unquote('-%s%s' % (self.host, self.path))\
                           .replace('/', ',').replace(':',',').replace(' ','_')
            ext = self.options.get('extension')
            
            if ext and not content_file.endswith(ext):
                content_file = content_file + ext
            
            if self.options.has_key('temp_dir'):
                while 1:
                    temp = path.expanduser(self.options['temp_dir'])
                    temp = os.tempnam(temp)
                    content_file = '%s%s' % (temp, content_file)
                    if not path.exists(content_file):
                        break
            else:
                content_file = mktemp(content_file)
                
            body_f = open(content_file, 'wb')
            body_f.write(in_f.read())
            self.content_file = content_file
            in_f.close()
            body_f.close()
            self.clean_up = int(self.options.get('cleanup_files', 1))
            if self.clean_up: os.remove(input_file)
        except:
            # for security, always delete the input file even if
            # a fatal error occurs, unless explicitly stated otherwise
            # in the config file
            if getattr(self, 'clean_up', 1):
                try:
                    exc, exc_data = sys.exc_info()[:2]
                    os.remove(input_file)
                except OSError:
                    # Sometimes we aren't allowed to delete it
                    raise exc, exc_data
            raise
        
    def __del__(self):
        # for security we always delete the files by default
        if getattr(self, 'clean_up', 1) and hasattr(self, 'content_file'):
            os.remove(self.content_file)
            
    def getEditorCommand(self):
        """Return the editor command"""
        editor = self.options.get('editor')
        """
        if not editor and has_tk():
            from tkSimpleDialog import askstring
            editor = askstring('Zope External Editor', 
                               'Enter the command to launch the default editor')
            if not editor: sys.exit(0)
            self.config.set('general', 'editor', path)
            self.config.save()
        """ 
        if editor is not None:            
            return editor
        else:
            fatalError('Editor not specified in configuration file.')
        
    def launch(self):
        """Launch external editor"""
        save_interval = float(self.options.get('save_interval'))
        use_locks = int(self.options.get('use_locks', 0))
        launch_success = 0
        last_mtime = path.getmtime(self.content_file)
        command = '%s %s' % (self.getEditorCommand(), self.content_file)
        editor = EditorProcess(command)
        
        if use_locks:
            self.lock()
            
        while 1:
            editor.wait(save_interval or 2)
            mtime = path.getmtime(self.content_file)
            
            if (save_interval or not editor.isAlive()) and mtime != last_mtime:
                # File was modified
                launch_success = 1 # handle very short editing sessions
                self.saved = self.putChanges()
                last_mtime = mtime

            if editor.isAlive():
                launch_success = 1
            else:
                break
                
        if not launch_success:
            fatalError('Editor did not launch properly.\n'
                       'External editor lost connection '
                       'to editor process.')
        
        if use_locks:
            self.unlock()
        
        if not self.saved \
           and askYesNo('File not saved to Zope.\nReopen local copy?'):
            self.launch()
        
    def putChanges(self):
        """Save changes to the file back to Zope"""
        if int(self.options.get('use_locks', 0)) and \
           not hasattr(self, 'lock_token'):
            # We failed to get a lock initially, so try again before saving
            if not self.lock():
                # Confirm save without lock
                if not askYesNo('Could not acquire lock. '
                                'Attempt to save to Zope anyway?'):
                    return 0
            
        f = open(self.content_file, 'rb')
        body = f.read()
        f.close()
        headers = {'Content-Type': 
                   self.metadata.get('content_type', 'text/plain')}
        
        if hasattr(self, 'lock_token'):
            headers['If'] = '<%s> (<%s>)' % (self.path, self.lock_token)
        
        response = self.zope_request('PUT', headers, body)
        del body # Don't keep the body around longer then we need to

        if response.status / 100 != 2:
            # Something went wrong
            sys.stderr.write('Error occurred during HTTP put:\n%d %s\n' \
                             % (response.status, response.reason))
            sys.stderr.write('\n----\n%s\n----\n' % response.read())
            message = response.getheader('Bobo-Exception-Type')
            
            if askRetryCancel('Could not save to Zope.\nError '
                              'occurred during HTTP put:\n%d %s\n%s' \
                              % (response.status, response.reason, message)):
                return self.putChanges()
            else:
                return 0
        return 1
    
    def lock(self):
        """Apply a webdav lock to the object in Zope"""
        
        headers = {'Content-Type':'text/xml; charset="utf-8"',
                   'Timeout':'infinite',
                   'Depth':'infinity',
                  }
        body = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<d:lockinfo xmlns:d="DAV:">\n'
                '  <d:lockscope><d:exclusive/></d:lockscope>\n'
                '  <d:locktype><d:write/></d:locktype>\n'
                '  <d:depth>infinity</d:depth>\n'
                '  <d:owner>\n' 
                '  <d:href>Zope External Editor</d:href>\n'
                '  </d:owner>\n'
                '</d:lockinfo>'
                )
        
        response = self.zope_request('LOCK', headers, body)
        
        if response.status / 100 == 2:
            # We got our lock, extract the lock token and return it
            reply = response.read()
            token_start = reply.find('>opaquelocktoken:')
            token_end = reply.find('<', token_start)
            if token_start > 0 and token_end > 0:
               self.lock_token = reply[token_start+1:token_end]
        else:
            # We can't lock her sir!
            if response.status == 423:
                message = '\n(Object already locked)'
            else:
                message = response.getheader('Bobo-Exception-Type')

            sys.stderr.write('Error occurred during lock request:\n%d %s\n' \
                             % (response.status, response.reason))
            sys.stderr.write('\n----\n%s\n----\n' % response.read())

            if askRetryCancel('Lock request failed:\n%d %s\n%s' \
                              % (response.status, response.reason, message)):
                return self.lock()
            else:
                return 0
        return 1
                    
    def unlock(self):
        """Remove webdav lock from edited zope object"""
        if not hasattr(self, 'lock_token'): 
            return 0
            
        headers = {'Lock-Token':self.lock_token}
        response = self.zope_request('UNLOCK', headers)
        
        if response.status / 100 != 2:
            # Captain, she's still locked!
            message = response.getheader('Bobo-Exception-Type')
            sys.stderr.write('Error occurred during unlock request:'
                             '\n%d %s\n%s\n' \
                             % (response.status, response.reason, message))
            sys.stderr.write('\n----\n%s\n----\n' % response.read())
            if askRetryCancel('Unlock request failed:\n%d %s'
                              % (response.status, response.reason)):
                return self.unlock(token)
            else:
                return 0
        return 1
        
    def zope_request(self, method, headers={}, body=''):
        """Send a request back to Zope"""
        try:
            if self.ssl:
                h = HTTPSConnection(self.host)
            else:
                h = HTTPConnection(self.host)

            h.putrequest(method, self.path)
            h.putheader('User-Agent', 'Zope External Editor/%s' % __version__)
            h.putheader('Connection', 'close')

            for header, value in headers.items():
                h.putheader(header, value)

            h.putheader("Content-Length", str(len(body)))

            if self.metadata.get('auth','').startswith('Basic'):
                h.putheader("Authorization", self.metadata['auth'])

            if self.metadata.get('cookie'):
                h.putheader("Cookie", self.metadata['cookie'])

            h.endheaders()
            h.send(body)
            return h.getresponse()
        except:
            # On error return a null response with error info
            class NullResponse:
                def getheader(n,d): return d
                def read(self): return '(No Response From Server)\n\n%s' \
                                       % sys.exc_info[2]
            
            response = NullResponse()
            response.reason = sys.exc_info()[1]
            try:
                response.status, response.reason = response.reason
            except:
                response.status = 0
            return response

title = 'Zope External Editor'

## Platform specific declarations ##

if win32:
    from win32ui import MessageBox
    from win32process import CreateProcess, GetExitCodeProcess, STARTUPINFO
    from win32event import WaitForSingleObject
    import pywintypes

    def errorDialog(message):
        MessageBox(message, title, 16)

    def askRetryCancel(message):
        return MessageBox(message, title, 53) == 4

    def askYesNo(message):
        return MessageBox(message, title, 52) == 6

    class EditorProcess:
        def __init__(self, command):
            """Launch editor process"""
            try:
                self.handle, ht, pid, tid = CreateProcess(None, command, None, 
                                                          None, 1, 0, None, 
                                                          None, STARTUPINFO())
            except pywintypes.error, e:
                fatalError('Error launching editor process\n'
                           '(%s):\n%s' % (command, e[2]))
        def wait(self, timeout):
            """Wait for editor to exit or until timeout"""
            WaitForSingleObject(self.handle, int(timeout * 1000.0))
                
        def isAlive(self):
            """Returns true if the editor process is still alive"""
            return GetExitCodeProcess(self.handle) == 259

else: # Posix platform
    from time import sleep

    def has_tk():
        """Sets up a suitable tk root window if one has not
           already been setup. Returns true if tk is happy,
           false if tk throws an error (like its not available)"""
        if not hasattr(globals(), 'tk_root'):
            # create a hidden root window to make Tk happy
            try:
                global tk_root
                from Tkinter import Tk
                tk_root = Tk()
                tk_root.withdraw()
                return 1
            except:
                return 0
        return 1

    def errorDialog(message):
        """Error dialog box"""
        try:
            if has_tk():
                from tkMessageBox import showerror
                showerror(title, message)
                has_tk()
        finally:
            sys.stderr.write(message)

    def askRetryCancel(message):
        if has_tk():
            from tkMessageBox import askretrycancel
            r = askretrycancel(title, message)
            has_tk() # ugh, keeps tk happy
            return r

    def askYesNo(message):
        if has_tk:
            from tkMessageBox import askyesno
            r = askyesno(title, message)
            has_tk() # must...make...tk...happy
            return r

    class EditorProcess:
        def __init__(self, command):
            """Launch editor process"""
            command = command.split()
            self.pid = os.spawnvp(os.P_NOWAIT, command[0], command)
        
        def wait(self, timeout):
            """Wait for editor to exit or until timeout"""
            sleep(timeout)
                
        def isAlive(self):
            """Returns true if the editor process is still alive"""
            try:
                exit_pid, exit_status = os.waitpid(self.pid, os.WNOHANG)
            except OSError:
                return 0
            else:
                return exit_pid != self.pid

def fatalError(message, exit=1):
    """Show error message and exit"""
    errorDialog('FATAL ERROR: %s' % message)
    if exit: 
        sys.exit(0)

def whereIs(filename): 
    """Given a filename, returns the full path to it based
       on the PATH environment variable. If no file was found, None is returned
    """
    pathExists = os.path.exists
    
    if pathExists(filename):
        return filename
        
    pathJoin = os.path.join
    paths = os.environ['PATH'].split(os.pathsep)
    
    for path in paths:
        file_path = pathJoin(path, filename)
        if pathExists(file_path):
            return file_path

default_configuration = """\
# Zope External Editor helper application configuration

[general]
# General configuration options

# Uncomment and specify an editor value to override the editor
# specified in the environment
#editor = 

# Automatic save interval, in seconds. Set to zero for
# no auto save (save to Zope only on exit).
save_interval = 1

# Temporary file cleanup. Set to false for debugging or
# to waste disk space. Note: setting this to false is a
# security risk to the zope server
cleanup_files = 1

# Use WebDAV locking to prevent concurrent editing by
# different users. Disable for single user use or for
# better performance
use_locks = 1

# Specific settings by content-type or meta-type. Specific
# settings override general options above. Content-type settings
# override meta-type settings for the same option.

[meta-type:DTML Document]
extension=.dtml

[meta-type:DTML Method]
extension=.dtml

[meta-type:Script (Python)]
extension=.py

[meta-type:Page Template]
extension=.pt

[meta-type:Z SQL Method]
extension=.sql

[content-type:text/*]
extension=.txt

[content-type:text/html]
extension=.html

[content-type:text/xml]
extension=.xml

[content-type:image/*]
editor=gimp

[content-type:image/gif]
extension=.gif

[content-type:image/jpeg]
extension=.jpg

[content-type:image/png]
extension=.png"""

if __name__ == '__main__':
    try:
        ExternalEditor(sys.argv[1]).launch()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except:
        fatalError(sys.exc_info()[1],0)
        raise
