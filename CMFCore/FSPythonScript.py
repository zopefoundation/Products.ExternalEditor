##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
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
        self._write(data, reparse)

    def _validateProxy(self, roles=None):
        pass

    #### The following is mainly taken from PythonScript.py ###

    def _exec(self, bound_names, args, kw):
        """Call a Python Script

        Calling a Python Script is an actual function invocation.
        """
        self._updateFromFS()
        # Prepare the function.
        f = self._v_f
        if f is None:
            # Not yet compiled.
            self._write(self._source, 1)
            f = self._v_f
            if f is None:
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
    def get_size(self): return len(self._body)

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
                fc = f.func_code
                self._setFuncSignature(f.func_defaults, fc.co_varnames,
                                       fc.co_argcount)
            else:
                # There were errors in the compile.
                self._setFuncSignature()  # No signature.
        self._body = ps._body
        self._params = ps._params
        self.title = ps.title
        self._setupBindings(ps.getBindingAssignments().getAssignedNames())
        self._source = ps.read()  # Find out what the script sees.

    def func_defaults(self):
        # This ensures func_code and func_defaults are
        # set when the code hasn't been compiled yet,
        # just in time for mapply().  Truly odd, but so is mapply(). :P
        self._write(self._source, 1)
        return self.__dict__.get('func_defaults', None)
    func_defaults = ComputedAttribute(func_defaults, 1)

    def func_code(self):
        # See func_defaults.
        self._write(self._source, 1)
        return self.__dict__.get('func_code', None)
    func_code = ComputedAttribute(func_code, 1)


Globals.InitializeClass(FSPythonScript)

registerFileExtension('py', FSPythonScript)
registerMetaType('Script (Python)', FSPythonScript)
