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
                  'action': 'string:document_view',
                  'permissions': (CMFCorePermissions.View,)},
                 {'name': 'Edit',
                  'action': 'string:document_edit_form',
                  'permissions': (CMFCorePermissions.ModifyPortalContent,)},
                 {'name': 'Metadata',
                  'action': 'string:metadata_edit_form',
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

    def _edit(self, text, text_format='', safety_belt=''):
        """ Edit the Document - Parses headers and cooks the body"""
        headers = {}
        if not text_format:
            text_format = self.text_format
        if not safety_belt:
            safety_belt = headers.get('SafetyBelt', '')
        if not self._safety_belt_update(safety_belt=safety_belt):
            msg = ("Intervening changes from elsewhere detected."
                   " Please refetch the document and reapply your changes."
                   " (You may be able to recover your version using the"
                   " browser 'back' button, but will have to apply them"
                   " to a freshly fetched copy.)")
            raise 'EditingConflict', msg
        self.cooked_text = self.cookText(text)
        self.text = text

    def cookText(self, text):
        return util.format_webtext(text)

    # XXX This is obsolete for CMF 1.2 Document.  It may be sufficient for
    # compatability with pre-CMF-1.2 Document architecture, but that's
    # untested.
    security.declarePrivate('handleText')
    def handleText(self, text, format=None, stx_level=None):
        """Handle the raw text, returning headers, body, cooked, format"""
        body = text
        cooked = self.cookText(text)
        headers = {}
        return headers, body, cooked, self.TEXT_FORMAT

InitializeClass(WebTextDocument)
