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
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

 
import Globals
from Globals import HTMLFile, HTML
from Discussions import Discussable
from Products.CMFCore.PortalContent import PortalContent
from DublinCore import DefaultDublinCoreImpl
from utils import parseHeadersBody

from Products.CMFCore import CMFCorePermissions

def addNewsItem( self
               , id
               , title=''
               , text=''
               , description=''
               , RESPONSE=None
               ):
    """
        Add a NewsItem
    """
    o=NewsItem( id, title, text, description )
    self._setObject(id,o)
    if RESPONSE is not None:
        RESPONSE.redirect(self.absolute_url()+'/folder_contents')


class NewsItem( PortalContent
              , DefaultDublinCoreImpl
              ):
    """
        A News Item
    """

    meta_type='News Item'
    effective_date = expiration_date = None
    _isDiscussable = 1

    __ac_permissions__=(
        (CMFCorePermissions.View, ('')),
        (CMFCorePermissions.ModifyPortalContent, ('edit',)),
        )

    def __init__( self
                , id
                , title=''
                , text=''
                , description=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.text=text
        self.description = description
        self._parse()

##    def __call__(self, REQUEST, **kw):
##        return apply(self.view, (self, REQUEST), kw)

    def edit( self, text, description ):
        """
            Edit the News Item
        """
        self.text=text
        self.description=description
        self._parse()
        self.reindexObject()

    def _parse(self):
        self.cooked_text=self._format_text(self)     
        
    _format_text=HTML('''<dtml-var text fmt="structured-text">''')

    def SearchableText(self):
        """
            text for indexing
        """
        return "%s %s %s" % (self.title, self.description, self.text)

    def Description(self):
        """
            description for indexing
        """
        return self.description

    ## FTP handlers

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP (and presumably FTP?) PUT requests"""
        try:
            self.dav__init(REQUEST, RESPONSE)

            headers = {}
            for k, v in self.getMetadataHeaders():
                if k != 'Format':
                    headers[k] = v

            body = REQUEST.get( 'BODY', '')
            headers, body = parseHeadersBody( body, headers )

            if not headers.has_key( 'Format' ): # not supplied in headers
                from NullPortalResource import sniffContentType
                sniffFmt = sniffContentType( self.id, body )
                fmt = REQUEST.get_header( 'content-type', sniffFmt )
                headers[ 'Format' ] = fmt

            self.editMetadata( title=headers['Title']
                             , subject=headers['Subject']
                             , description=headers['Description']
                             , contributors=headers['Contributors']
                             , effective_date=headers['Effective_date']
                             , expiration_date=headers['Expiration_date']
                             , format=headers['Format']
                             , language=headers['Language']
                             , rights=headers['Rights']
                             )
            self.edit( title=self.Title()
                     , description=self.Description()
                     , text=body
                     )
            RESPONSE.setStatus(204)
            return RESPONSE
        except:
            import traceback
            traceback.print_exc()
            raise

    def manage_FTPget(self):
        "Get the document body for FTP download"
        from string import join
        hdrlist = self.getMetadataHeaders()
        hdrtext = join( map( lambda x: '%s: %s' % ( x[0], x[1] )
                           , hdrlist
                           )
                      , '\n'
                      )
        return '%s\n\n%s' % ( hdrtext, self.text )

Globals.default__class_init__(NewsItem)

from Products.CMFCore.register import registerPortalContent
registerPortalContent(NewsItem,
                      constructors=(addNewsItem,),
                      action='Wizards/NewsItem',
                      icon="newsitem.gif",
                      productGlobals=globals())
