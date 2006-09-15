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
"""Zope External Editor Helper Application by Casey Duncan

$Id$"""

__version__ = '0.9.2'

import sys

win32 = sys.platform == 'win32'

if win32:
    # prevent warnings from being turned into errors by py2exe
    import warnings
    warnings.filterwarnings('ignore')

import os, re
import rfc822
import traceback
from tempfile import mktemp
from ConfigParser import ConfigParser
from httplib import HTTPConnection, HTTPSConnection
from urlparse import urlparse
import urllib

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
    
    did_lock = 0
    
    def __init__(self, input_file):
        try:
            # Read the configuration file
            if win32:
                # Check the home dir first and then the program dir
                config_path = os.path.expanduser('~\\ZopeEdit.ini')
                global_config = os.path.join(sys.path[0] or '', 'ZopeEdit.ini')
                if not os.path.exists(config_path) \
                   and os.path.exists(global_config):
                    config_path = global_config
            else:
                config_path = os.path.expanduser('~/.zope-external-edit')
                
            self.config = Configuration(config_path)

            # Open the input file and read the metadata headers
            in_f = open(input_file, 'rU')
            m = rfc822.Message(in_f)

            self.metadata = metadata = m.dict.copy()
                               
            # parse the incoming url
            scheme, self.host, self.path = urlparse(metadata['url'])[:3]
            self.ssl = scheme == 'https'
            
            # Get all configuration options
            self.options = self.config.getAllOptions(
                                            metadata['meta_type'],
                                            metadata.get('content_type',''),
                                            self.host)

            # Write the body of the input file to a separate file
            if int(self.options.get('long_file_name', 1)):
                sep = self.options.get('file_name_separator', ',')
                content_file = urllib.unquote('-%s%s' % (self.host, self.path))
                content_file = content_file.replace(
                    '/', sep).replace(':',sep).replace(' ','_')
            else:
                content_file = '-' + urllib.unquote(self.path.split('/')[-1])
                
            extension = self.options.get('extension')
            if extension and not content_file.endswith(extension):
                content_file = content_file + extension
            
            if self.options.has_key('temp_dir'):
                while 1:
                    temp = os.path.expanduser(self.options['temp_dir'])
                    temp = os.tempnam(temp)
                    content_file = '%s%s' % (temp, content_file)
                    if not os.path.exists(content_file):
                        break
            else:
                content_file = mktemp(content_file)
                
            body_f = open(content_file, 'wb')
            body_f.write(in_f.read())
            self.content_file = content_file
            self.saved = 1
            in_f.close()
            body_f.close()
            self.clean_up = int(self.options.get('cleanup_files', 1))
            if self.clean_up: 
                try:
                    os.remove(input_file)
                except OSError:
                    pass # Sometimes we aren't allowed to delete it
            
            if self.ssl:
                # See if ssl is available
                try:
                    from socket import ssl
                except ImportError:
                    fatalError('SSL support is not available on this system. '
                               'Make sure openssl is installed '
                               'and reinstall Python.')
            self.lock_token = None
            self.did_lock = 0
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
        if getattr(self, 'clean_up', 1) and hasattr(self, 'content_file'):
            # for security we always delete the files by default
            try:
                os.remove(self.content_file)
            except OSError:
                pass     

        if self.did_lock:
            # Try not to leave dangling locks on the server
            self.unlock(interactive=0)
            
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

                    if editor is None:
                        # Enumerate the actions looking for one
                        # starting with 'Edit'
                        try:
                            key = OpenKeyEx(HKEY_CLASSES_ROOT, 
                                            classname+'\\Shell')
                            index = 0
                            while 1:
                                try:
                                    subkey = EnumKey(key, index)
                                    index += 1
                                    if str(subkey).lower().startswith('edit'):
                                        subkey = OpenKeyEx(key, 
                                                           subkey + 
                                                           '\\Command')
                                        editor, nil = QueryValueEx(subkey, 
                                                                   None)
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
                        nil, editor = FindExecutable(self.content_file, '')
                    except pywintypes.error:
                        pass
            
            # Don't use IE as an "editor"
            if editor is not None and editor.find('\\iexplore.exe') != -1:
                editor = None

        if editor is not None:            
            return editor
        else:
            fatalError('No editor was found for that object.\n'
                       'Specify an editor in the configuration file:\n'
                       '(%s)' % self.config.path)
        
    def launch(self):
        """Launch external editor"""
        use_locks = int(self.options.get('use_locks', 0))
        if use_locks and self.metadata.get('lock-token'):
            # A lock token came down with the data, so the object is
            # already locked, see if we can borrow the lock
            if (int(self.options.get('always_borrow_locks', 0))
                or self.metadata.get('borrow_lock')
                or askYesNo('This object is already locked by you in another'
                            ' session.\n Do you want to borrow this lock'
                            ' and continue?')):
                self.lock_token = 'opaquelocktoken:%s' \
                                  % self.metadata['lock-token']
            else:
                sys.exit()            
        
        save_interval = float(self.options.get('save_interval'))
        last_mtime = os.path.getmtime(self.content_file)
        command = self.getEditorCommand()

        # Extract the executable name from the command
        if win32:
            if command.find('\\') != -1:
                bin = re.search(r'\\([^\.\\]+)\.exe', command.lower())
                if bin is not None:
                    bin = bin.group(1)
            else:
                bin = command.lower().strip()
        else:
            bin = command

        if bin is not None:
            # Try to load the plugin for this editor
            try:
                module = 'Plugins.%s' % bin
                Plugin = __import__(module, globals(), locals(), 
                                    ('EditorProcess',))
                editor = Plugin.EditorProcess(self.content_file)
            except (ImportError, AttributeError):
                bin = None

        if bin is None: 
            # Use the standard EditorProcess class for this editor
            if win32:
                file_insert = '%1'
            else:
                file_insert = '$1'
                
            if command.find(file_insert) > -1:
                command = command.replace(file_insert, self.content_file)
            else:
                command = '%s %s' % (command, self.content_file)

            editor = EditorProcess(command)
            
        launch_success = editor.isAlive()
        
        if use_locks:
            self.lock()

        final_loop = 0
	    
        while 1:
            if not final_loop:
                editor.wait(save_interval or 2)

            mtime = os.path.getmtime(self.content_file)

            if mtime != last_mtime:
                if save_interval or final_loop:
                    launch_success = 1 # handle very short editing sessions
                    self.saved = self.putChanges()
                    last_mtime = mtime

            if not editor.isAlive():
                if final_loop:
                    break
                else:
                    # Go through the loop one final time for good measure.
                    # Our editor's isAlive method may itself *block* during a
                    # save operation (seen in COM calls, which seem to
                    # respond asynchronously until they don't) and subsequently
                    # return false, but the editor may have actually saved the
                    # file to disk while the call blocked.  We want to catch
                    # any changes that happened during a blocking isAlive call.
                    final_loop = 1

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
        if int(self.options.get('use_locks', 0)) and self.lock_token is None:
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
        
        if self.lock_token is not None:
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
        if self.lock_token is not None:
            return 0 # Already have a lock token
        
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
                self.did_lock = 1
        else:
            # We can't lock her sir!
            if response.status == 423:
                message = '(object already locked)'
            else:
                message = ''
                
            if self.askRetryAfterError(response, 
                                       'Lock request failed', 
                                       message):
                self.lock()
            else:
                self.did_lock = 0
        return self.did_lock
                    
    def unlock(self, interactive=1):
        """Remove webdav lock from edited zope object"""
        if not self.did_lock or self.lock_token is None:
            return 0 # nothing to do
            
        headers = {'Lock-Token':self.lock_token}
        response = self.zopeRequest('UNLOCK', headers)
        
        if interactive and response.status / 100 != 2:
            # Captain, she's still locked!
            if self.askRetryAfterError(response, 'Unlock request failed'):
                self.unlock()
            else:
                self.did_lock = 0
        else:
            self.did_lock = 1
            self.lock_token = None
        return self.did_lock
        
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

            if self.metadata.get('auth','').lower().startswith('basic'):
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
            
            try:
                response.status, response.reason = response.reason
            except ValueError:
                response.status = 0
            
            if response.reason == 'EOF occurred in violation of protocol':
                # Ignore this protocol error as a workaround for
                # broken ssl server implementations
                response.status = 200
                
            return response
            
    def askRetryAfterError(self, response, operation, message=''):
        """Dumps response data"""
        if not message \
           and response.getheader('Bobo-Exception-Type') is not None:
            message = '%s: %s' % (response.getheader('Bobo-Exception-Type'),
                                  response.getheader('Bobo-Exception-Value'))
        return askRetryCancel('%s:\n%d %s\n%s' % (operation, response.status, 
                                               response.reason, message))

title = 'Zope External Editor'

## Platform specific declarations ##

if win32:
    import Plugins # Assert dependancy
    from win32ui import MessageBox
    from win32process import CreateProcess, GetExitCodeProcess, STARTUPINFO
    from win32event import WaitForSingleObject
    from win32con import MB_OK, MB_OKCANCEL, MB_YESNO, MB_RETRYCANCEL, \
                         MB_SYSTEMMODAL, MB_ICONERROR, MB_ICONQUESTION, \
                         MB_ICONEXCLAMATION
    import pywintypes

    def errorDialog(message):
        MessageBox(message, title, MB_OK + MB_ICONERROR + MB_SYSTEMMODAL)

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
    import re

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
            print message

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
            # Prepare the command arguments, we use this regex to 
            # split on whitespace and properly handle quoting
            arg_re = r"""\s*([^'"]\S+)\s+|\s*"([^"]+)"\s*|\s*'([^']+)'\s*"""
            args = re.split(arg_re, command.strip())
            args = filter(None, args) # Remove empty elements
            self.pid = os.spawnvp(os.P_NOWAIT, args[0], args)
        
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
    # Write out debug info to a temp file
    debug_f = open(mktemp('-zopeedit-traceback.txt'), 'w')
    try:
        traceback.print_exc(file=debug_f)
    finally:
        debug_f.close()
    if exit: 
        sys.exit(0)

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

# To suppress warnings about borrowing locks on objects
# locked by you before you began editing you can
# set this flag. This is useful for applications that
# use server-side locking, like CMFStaging
always_borrow_locks = 0

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

[content-type:text/plain]
extension=.txt

[content-type:text/html]
extension=.html

[content-type:text/xml]
extension=.xml

[content-type:text/css]
extension=.css

[content-type:text/javascript]
extension=.js

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
        args = sys.argv
        
        if '--version' in args or '-v' in args:
            credits = ('Zope External Editor %s\n'
                       'By Casey Duncan, Zope Corporation\n'
                       'http://www.zope.com/') % __version__
            if win32:
                errorDialog(credits)
            else:
                print credits
            sys.exit()

        input_file = sys.argv[1]
    except IndexError:
        fatalError('Input file name missing.\n'
                   'Usage: zopeedit inputfile')
    try:
        ExternalEditor(input_file).launch()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except:
        fatalError(sys.exc_info()[1])
