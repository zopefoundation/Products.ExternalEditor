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
"""Customizable Python scripts that come from the filesystem."""
__version__='$Revision$'[11:-2]

from string import strip, split
from os import path, stat
import new

import Globals
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.PythonScripts.PythonScript import PythonScript
from Shared.DC.Scripts.Script import Script
from ComputedAttribute import ComputedAttribute

from utils import _dtmldir
from CMFCorePermissions import ViewManagementScreens, View, FTPAccess
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from FSObject import FSObject

class FSPythonScript (FSObject, Script):
    """FSPythonScripts act like Python Scripts but are not directly
    modifiable from the management interface."""

    meta_type = 'Filesystem Script (Python)'
    _params = _body = ''
    _v_f = None

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test',
             'action':'ZScriptHTML_tryForm',
             'help': ('PythonScripts', 'PythonScript_test.stx')},
            )
        )

    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    security.declareProtected(View, 'index_html',)
    # Prevent the bindings from being edited TTW
    security.declarePrivate('ZBindings_edit','ZBindingsHTML_editForm','ZBindingsHTML_editAction')

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custpy', _dtmldir)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = PythonScript(self.getId())
        obj.write(self.read())
        return obj

    def _readFile(self, reparse):
        """Read the data from the filesystem.
        
        Read the file (indicated by exandpath(self._filepath), and parse the
        data if necessary.
        """
        fp = expandpath(self._filepath)
        file = open(fp, 'r')
        try: data = file.read()
        finally: file.close()
        if reparse:
            self._write(data, reparse)

    def _validateProxy(self, roles=None):
        pass

    def __render_with_namespace__(self, namespace):
        '''Calls the script.'''
        self._updateFromFS()
        return Script.__render_with_namespace__(self, namespace)

    def __call__(self, *args, **kw):
        '''Calls the script.'''
        self._updateFromFS()
        return Script.__call__(self, *args, **kw)

    #### The following is mainly taken from PythonScript.py ###

    def _exec(self, bound_names, args, kw):
        """Call a Python Script

        Calling a Python Script is an actual function invocation.
        """
        # Prepare the function.
        f = self._v_f
        if f is None:
            # The script has errors.
            raise RuntimeError, '%s has errors.' % self._filepath

        __traceback_info__ = bound_names, args, kw, self.func_defaults

        if bound_names:
            # Updating func_globals directly is not thread safe here.
            # In normal PythonScripts, every thread has its own
            # copy of the function.  But in FSPythonScripts
            # there is only one copy.  So here's another way.
            new_globals = f.func_globals.copy()
            new_globals.update(bound_names)
            if f.func_defaults:
                f = new.function(f.func_code, new_globals, f.func_name,
                                 f.func_defaults)
            else:
                f = new.function(f.func_code, new_globals, f.func_name)

        # Execute the function in a new security context.
        security=getSecurityManager()
        security.addContext(self)
        try:
            result = apply(f, args, kw)
            return result
        finally:
            security.removeContext(self)

    security.declareProtected(ViewManagementScreens,
      'read', 'getModTime', 'get_size',
      'ZScriptHTML_tryForm', 'PrincipiaSearchSource',
      'document_src', 'params', 'body')

    def ZScriptHTML_tryParams(self):
        """Parameters to test the script with."""
        param_names = []
        for name in split(self._params, ','):
            name = strip(name)
            if name and name[0] != '*':
                param_names.append(split(name, '=', 1)[0])
        return param_names

    def read(self):
        self._updateFromFS()
        return self._source
                
    def document_src(self, REQUEST=None, RESPONSE=None):
        """Return unprocessed document source."""

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/plain')
        return self._source

    def PrincipiaSearchSource(self):
        "Support for searching - the document's contents are searched."
        return "%s\n%s" % (self._params, self._body)

    def params(self): return self._params
    def body(self): return self._body
    def get_size(self): return len(self.read())

    security.declareProtected(FTPAccess, 'manage_FTPget')
    def manage_FTPget(self):
        "Get source for FTP download"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        return self.read()

    def _write(self, text, compile):
        '''
        Parses the source, storing the body, params, title, bindings,
        and source in self.  If compile is set, compiles the
        function.
        '''
        ps = PythonScript(self.id)
        ps.write(text)
        if compile:
            ps._makeFunction(1)
            self._v_f = f = ps._v_f
            if f is not None:
                self.func_code = f.func_code
                self.func_defaults = f.func_defaults
            else:
                # There were errors in the compile.
                # No signature.
                self.func_code = None
                self.func_defaults = None
        self._body = ps._body
        self._params = ps._params
        self.title = ps.title
        self._setupBindings(ps.getBindingAssignments().getAssignedNames())
        self._source = ps.read()  # Find out what the script sees.

    def func_defaults(self):
        # This ensures func_code and func_defaults are
        # set when the code hasn't been compiled yet,
        # just in time for mapply().  Truly odd, but so is mapply(). :P
        self._updateFromFS()
        return self.__dict__.get('func_defaults', None)
    func_defaults = ComputedAttribute(func_defaults, 1)

    def func_code(self):
        # See func_defaults.
        self._updateFromFS()
        return self.__dict__.get('func_code', None)
    func_code = ComputedAttribute(func_code, 1)

    def title(self):
        # See func_defaults.
        self._updateFromFS()
        return self.__dict__.get('title', None)
    title = ComputedAttribute(title, 1)


Globals.InitializeClass(FSPythonScript)

registerFileExtension('py', FSPythonScript)
registerMetaType('Script (Python)', FSPythonScript)
