##############################################################################
# Copyright (c) 2001 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 1.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
##############################################################################

"""A Document derivative for presenting plain text on the web.

 - Paragraphs of contiguous lines at the left margin are flowed until hard
   newlines.
 - Indented and '>' cited lines are presented exactly, preserving whitespace.
 - URLs (outside indented and cited literal regions) are turned into links.
 - Character entities outside of linkified URLs are html-quoted.

This makes it easy to present both flowed paragraphs and source code (and
other literal text), without having to know and navigate the nuances of HTML
and/or structured text."""

import os, urllib, string, re
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base

import util                             # Collector utilities.

from Products.CMFDefault.Document import Document
from Products.CMFDefault.utils import SimpleHTMLParser, bodyfinder

from Products.CMFCore import CMFCorePermissions
from CollectorPermissions import *

factory_type_information = (
    {'id': 'WebText Document',
     'meta_type': 'WebText Document',
     'icon': 'document_icon.gif',
     'description': ('A document for simple text, with blank-line delimited'
                     ' paragraphs and special (indented, cited text)'
                     ' preformatting.'),
     'product': 'CMFCollector',
     'factory': None,                   # XXX Register add method when blessed.
     'immediate_view': 'metadata_edit_form',
     # XXX May need its own forms, in order to inhibit formatting option.
     'actions': ({'name': 'View',
                  'action': 'document_view',
                  'permissions': (CMFCorePermissions.View,)},
                 {'name': 'Edit',
                  'action': 'document_edit_form',
                  'permissions': (CMFCorePermissions.ModifyPortalContent,)},
                 {'name': 'Metadata',
                  'action': 'metadata_edit_form',
                  'permissions': (CMFCorePermissions.ModifyPortalContent,)},
                 ),
     },
    )

def addWebTextDocument(self, id, title='', description='', text_format='',
                       text=''):
    """ Add a WebText Document """
    o = WebTextDocument(id, title=title, description=description,
                        text_format=text_format, text=text)
    self._setObject(id,o)

class WebTextDocument(Document):
    __doc__                             # Use the module documentation.

    meta_type = 'WebText Document'
    TEXT_FORMAT = 'webtext'
    text_format = TEXT_FORMAT

    _stx_level = 0

    security = ClassSecurityInfo()

    def __init__(self, id, title='', description='', text_format='',
                 text=''):
        Document.__init__(self, id, title=title, description=description,
                          text_format=text_format or self.text_format,
                          text=text)
        self.text_format = text_format or self.TEXT_FORMAT

    security.declarePrivate('guessFormat')
    def guessFormat(self, text):
        """Infer inner document content type."""
        # Respect the registered text_format, if we can, else sniff.
        if string.lower(self.text_format) == self.TEXT_FORMAT:
            return self.TEXT_FORMAT
        elif string.lower(self.text_format) == 'html':
            return 'text/html'
        elif string.lower(self.text_format) in ['stx', 'structuredtext',
                                                'structured-text',
                                                'structured_text']:
            return 'structured-text'
        else:
            return Document.guessFormat(self, text)

    def _edit(self, text_format, text, file='', safety_belt=''):
        got = Document._edit(self, text_format or self.text_format,
                             text=text, file=file, safety_belt=safety_belt)
        # The document stubbornly insists on a text format it likes, despite
        # our explicit specification - set it back:
        self.text_format = text_format or self.TEXT_FORMAT

    security.declarePrivate('handleText')
    def handleText(self, text, format=None, stx_level=None):
        """Handle the raw text, returning headers, body, cooked, format"""
        if not format:
            format = self.guessFormat(text)
        if format != self.TEXT_FORMAT:
            return Document.handleText(self, text, format=format,
                                       stx_level=stx_level or self._stx_level)
        else:
            body = text
            cooked = util.format_webtext(body)
            headers = {}
            return headers, body, cooked, format

InitializeClass(WebTextDocument)
