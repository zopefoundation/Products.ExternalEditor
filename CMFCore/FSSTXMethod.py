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
"""
    Export "methodish" STXDocument class, intended for use as
    an element in the skin of a CMFSite.
"""

from string import split
from os import path, stat
import re

import Globals
from AccessControl import ClassSecurityInfo, getSecurityManager, Permissions
from OFS.DTMLMethod import DTMLMethod, decapitate, guess_content_type

from utils import _dtmldir, _format_stx
import CMFCorePermissions
import StructuredText
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from FSObject import FSObject


class FSSTXMethod( FSObject ):
    """
        A chunk of StructuredText, rendered as a skin method of a
        CMFSite.
    """

    meta_type = 'Filesystem STX Method'

    manage_options=( { 'label'      : 'Customize'
                     , 'action'     : 'manage_main'
                     }
                   , { 'label'      : 'View'
                     , 'action'     : ''
                     , 'help'       : ('OFSP'
                                      ,'DTML-DocumentOrMethod_View.stx'
                                      )
                     }
                   )

    security = ClassSecurityInfo()
    security.declareObjectProtected( CMFCorePermissions.View )

    security.declareProtected( CMFCorePermissions.ViewManagementScreens
                             , 'manage_main')
    manage_main = Globals.DTMLFile( 'custstx', _dtmldir )

    #
    #   FSObject interface
    #
    def _createZODBClone(self):
        """
            Create a ZODB (editable) equivalent of this object.
        """
        # XXX:  do this soon
        raise NotImplemented, "See next week's model."

    def _readFile( self, reparse ):

        fp = expandpath( self._filepath )
        file = open( fp, 'r' )  # not binary, we want CRLF munging here.

        try:
            data = file.read()
        finally:
            file.close()

        self.raw = data

        if reparse:
            self.cook()

    #
    #   "Wesleyan" interface (we need to be "methodish").
    #
    class func_code:
        pass

    func_code=func_code()
    func_code.co_varnames= ()
    func_code.co_argcount=0
    func_code.__roles__=()
    
    func_defaults__roles__=()
    func_defaults=()

    index_html = None   # No accidental acquisition

    default_content_type = 'text/html'

    def cook( self ):
        if not hasattr( self, '_v_cooked' ):
            self._v_cooked = _format_stx( text=self.raw )
        return self._v_cooked

    _default_template = Globals.HTML( """\
<dtml-var standard_html_header>
<div class="Desktop">
<dtml-var cooked>
</div>
<dtml-var standard_html_footer>""" )

    def __call__( self, REQUEST={}, RESPONSE=None, **kw ):
        """
            Return our rendered StructuredText.
        """
        self._updateFromFS()

        if RESPONSE is not None:
            RESPONSE.setHeader( 'Content-Type', 'text/html' )
        return apply( self._render, ( REQUEST, RESPONSE ), kw )

    security.declarePrivate( '_render' )
    def _render( self, REQUEST={}, RESPONSE=None, **kw ):
        """
            Find the appropriate rendering template and use it to
            render us.
        """
        template = getattr( self, 'stxmethod_view', self._default_template )

        if getattr( template, 'isDocTemp', 0 ):
            posargs = ( self, REQUEST )
        else:
            posargs = ()
        
        return apply( template, posargs, { 'cooked' : self.cook() } )

    security.declareProtected( CMFCorePermissions.FTPAccess, 'manage_FTPget' )
    def manage_FTPget( self ):
        """
            Fetch our source for delivery via FTP.
        """
        return self.raw

    security.declareProtected( CMFCorePermissions.ViewManagementScreens
                             , 'PrincipiaSearchSource' )
    def PrincipiaSearchSource( self ):
        """
            Fetch our source for indexing in a catalog.
        """
        return self.raw

    security.declareProtected( CMFCorePermissions.ViewManagementScreens
                             , 'document_src' )
    def document_src( self ):
        """
            Fetch our source for indexing in a catalog.
        """
        return self.raw

Globals.InitializeClass( FSSTXMethod )

registerFileExtension( 'stx', FSSTXMethod )
registerMetaType( 'STX Method', FSSTXMethod )
