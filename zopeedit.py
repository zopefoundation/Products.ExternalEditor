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
import traceback
from tempfile import mktemp
from ConfigParser import ConfigParser
from httplib import HTTPConnection, HTTPSConnection, HTTPException
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

        sections = ['general']
        sections.extend(domains)
        sections.append('meta-type:%s' % meta_type)
        sections.append('content-type:%s' % general_type)
        sections.append('content-type:%s' % content_type)
        
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
                config_path = path.expanduser('~\ZopeEdit.ini')
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
            extension = self.options.get('extension')
            
            if extension and not content_file.endswith(extension):
                content_file = content_file + extension
            
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
            if self.clean_up: 
                try:
                    os.remove(input_file)
                except OSError:
                    pass # Sometimes we aren't allowed to delete it
            
            if self.ssl:
                # See if our Python build supports ssl
                try:
                    from socket import ssl
                except ImportError:
                    fatalError('SSL support is not available on this system. '
                               'Make sure openssl is installed '
                               'and reinstall Python.')
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
        
        if win32 and editor is None:
            from _winreg import HKEY_CLASSES_ROOT, OpenKeyEx, \
                                QueryValueEx, EnumKey
            from win32api import FindExecutable
            import pywintypes
            # Find editor application based on mime type and extension
            content_type = self.metadata.get('content_type')
            extension = self.options.get('extension')
            
            if content_type:
                # Search registry for the extension by MIME type
                try:
                    key = 'MIME\\Database\\Content Type\\%s' % content_type
                    key = OpenKeyEx(HKEY_CLASSES_ROOT, key)
                    extension, nil = QueryValueEx(key, 'Extension')
                except EnvironmentError:
                    pass
            
            if extension is None:
                url = self.metadata['url']
                dot = url.rfind('.')

                if dot != -1 and dot > url.rfind('/'):
                    extension = url[dot:]

            if extension is not None:
                try:
                    key = OpenKeyEx(HKEY_CLASSES_ROOT, extension)
                    classname, nil = QueryValueEx(key, None)
                except EnvironmentError:
                    classname = None

                if classname is not None:
                    try:
                        # Look for Edit action in registry
                        key = OpenKeyEx(HKEY_CLASSES_ROOT, 
                                        classname+'\\Shell\\Edit\\Command')
                        editor, nil = QueryValueEx(key, None)
                    except EnvironmentError:
                        pass

                if classname is not None and editor is None:
                    # Enumerate the actions looking for one
                    # starting with 'Edit'
                    try:
                        key = OpenKeyEx(HKEY_CLASSES_ROOT, classname+'\\Shell')
                        index = 0
                        while 1:
                            try:
                                subkey = EnumKey(key, index)
                                index += 1
                                if str(subkey).lower().startswith('edit'):
                                    subkey = OpenKeyEx(key, 
                                                       subkey + '\\Command')
                                    editor, nil = QueryValueEx(subkey, None)
                                else:
                                    continue
                            except EnvironmentError:
                                break
                    except EnvironmentError:
                        pass

                if editor is None:
                    try:
                        # Look for Open action in registry
                        key = OpenKeyEx(HKEY_CLASSES_ROOT, 
                                        classname+'\\Shell\\Open\\Command')
                        editor, nil = QueryValueEx(key, None)
                    except EnvironmentError:
                        pass

                if editor is None:
                    try:
                        nil, editor = FindExecutable(self.body_file, '')
                    except pywintypes.error:
                        pass
            
            # Don't use IE as an "editor"
            if editor is not None and editor.find('\\iexplore.exe') != -1:
                editor = None

        if not editor and not win32 and has_tk():
            from tkSimpleDialog import askstring
            editor = askstring('Zope External Editor', 
                               'Enter the command to launch the default editor')
            if not editor: 
                sys.exit(0)
            self.config.set('general', 'editor', path)
            self.config.save()

        if editor is not None:            
            return editor
        else:
            fatalError('No editor was found for that object.\n'
                       'Specify an editor in the configuration file.')
        
    def launch(self):
        """Launch external editor"""
        save_interval = float(self.options.get('save_interval'))
        use_locks = int(self.options.get('use_locks', 0))
        launch_success = 0
        last_mtime = path.getmtime(self.content_file)
        command = self.getEditorCommand()
        if command.find('%1') > -1:
            command = command.replace('%1', self.content_file)
        else:
            command = '%s %s' % (command, self.content_file)
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
                       'to editor process.\n'
                       '(%s)' % command)
        
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
        
        response = self.zopeRequest('PUT', headers, body)
        del body # Don't keep the body around longer then we need to

        if response.status / 100 != 2:
            # Something went wrong
            if self.askRetryAfterError(response, 
                                       'Could not save to Zope.\n'
                                       'Error occurred during HTTP put'):
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
        
        response = self.zopeRequest('LOCK', headers, body)
        
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
                message = '(object already locked)'
            else:
                message = ''
                
            if self.askRetryAfterError(response, 
                                       'Lock request failed', 
                                       message):
                return self.lock()
            else:
                return 0
        return 1
                    
    def unlock(self):
        """Remove webdav lock from edited zope object"""
        if not hasattr(self, 'lock_token'): 
            return 0
            
        headers = {'Lock-Token':self.lock_token}
        response = self.zopeRequest('UNLOCK', headers)
        
        if response.status / 100 != 2:
            # Captain, she's still locked!
            if self.askRetryAfterError(response, 
                                       'Unlock request failed'):
                return self.unlock(token)
            else:
                return 0
        return 1
        
    def zopeRequest(self, method, headers={}, body=''):
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
                def getheader(self, n, d=None):
                    return d
                    
                def read(self): 
                    return '(No Response From Server)'
            
            response = NullResponse()
            response.reason = sys.exc_info()[1]
            sys.stderr.write('\n-- Zope Request Traceback --\n')
            traceback.print_exc(file=sys.stderr)
            
            try:
                response.status, response.reason = response.reason
            except ValueError:
                response.status = 0
            
            return response
            
    def askRetryAfterError(self, response, operation, message=''):
        """Dumps response data to stderr"""
        if not message \
           and response.getheader('Bobo-Exception-Type') is not None:
            message = '%s: %s' % (response.getheader('Bobo-Exception-Type'),
                                  response.getheader('Bobo-Exception-Value'))
                                  
        sys.stderr.write('Error occurred: %s:\n%d %s\n%s\n'
                         % (operation, response.status, 
                            response.reason, message))
                            
        if hasattr(response, 'msg'):
            headers = ''.join(response.msg.headers)
        else:
            headers = ''
            
        sys.stderr.write('\n----\n%s\n%s\n----\n' % (headers, response.read()))
        return askRetryCancel('%s:\n%d %s\n%s' % (operation, response.status, 
                                               response.reason, message))

title = 'Zope External Editor'

## Platform specific declarations ##

if win32:
    from win32ui import MessageBox
    from win32process import CreateProcess, GetExitCodeProcess, STARTUPINFO
    from win32event import WaitForSingleObject
    from win32con import MB_OK, MB_OKCANCEL, MB_YESNO, MB_RETRYCANCEL, \
                         MB_SYSTEMMODAL, MB_ICONERROR, MB_ICONQUESTION, \
                         MB_ICONEXCLAMATION
    import pywintypes

    def errorDialog(message):
        MessageBox(message, title, MB_OK + MB_ICONERROR + MB_SYSTEMMODAL)
        sys.stderr.write(message + '\n')

    def askRetryCancel(message):
        return MessageBox(message, title, 
                          MB_OK + MB_RETRYCANCEL + MB_ICONEXCLAMATION 
                          + MB_SYSTEMMODAL) == 4

    def askYesNo(message):
        return MessageBox(message, title, 
                          MB_OK + MB_YESNO + MB_ICONQUESTION +
                          MB_SYSTEMMODAL) == 6

    class EditorProcess:
        def __init__(self, command):
            """Launch editor process"""
            try:
                self.handle, nil, nil, nil = CreateProcess(None, command, None, 
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
            # create a hidden root window to make Tk happy
        if not locals().has_key('tk_root'):
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
            sys.stderr.write(message + '\n')

    def askRetryCancel(message):
        if has_tk():
            from tkMessageBox import askretrycancel
            r = askretrycancel(title, message)
            has_tk() # ugh, keeps tk happy
            return r

    def askYesNo(message):
        if has_tk():
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
    traceback.print_exc(file=sys.stderr)
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
        input_file = sys.argv[1]
    except IndexError:
        fatalError('Input file name missing.\n'
                   'Usage: zopeedit.py inputfile')
    try:
        ExternalEditor(input_file).launch()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except:
        fatalError(sys.exc_info()[1])
