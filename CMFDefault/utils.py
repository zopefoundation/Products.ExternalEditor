"""
    Utility functions.
"""
from string import split, join, lstrip, lower, strip, capitalize
from sgmllib import SGMLParser
import re
import os
from Globals import package_home
_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

def parseHeadersBody( body, headers=None ):
    """
        Parse any leading 'RFC-822'-ish headers from an uploaded
        document, returning a dictionary containing the headers
        and the stripped body.

        E.g.::

            Title: Some title
            Creator: Tres Seaver
            Format: text/plain
            X-Text-Format: structured

            Overview

            This document .....

            First Section

            ....


        would be returned as::

            { 'Title' : 'Some title'
            , 'Creator' : 'Tres Seaver'
            , 'Format' : 'text/plain'
            , 'text_format': 'structured'
            }

        as the headers, plus the body, starting with 'Overview' as
        the first line (the intervening blank line is a separator).

        Allow passing initial dictionary as headers.
    """
    # Split the lines apart, taking into account Mac|Unix|Windows endings
    lines = re.split(r'[\n\r]+?', body)

    i = 0
    if headers is None:
        headers = {}
    else:
        headers = headers.copy()

    hdrlist = []
    for line in lines:
        if line and line[-1] == '\r':
            line = line[:-1]
        if not line:
            break
        tokens = split( line, ': ' )
        if len( tokens ) > 1:
            hdrlist.append( ( tokens[0], join( tokens[1:], ': ' ) ) )
        elif i == 0:
            return headers, body     # no headers, just return those passed in.
        else:    # continuation
            last, hdrlist = hdrlist[ -1 ], hdrlist[ :-1 ]
            hdrlist.append( ( last[ 0 ]
                            , join( ( last[1], lstrip( line ) ), '\n' )
                            ) )
        i = i + 1

    for hdr in hdrlist:
        headers[ hdr[0] ] = hdr[ 1 ]

    return headers, join( lines[ i+1: ], '\n' )


    
def tuplize( valueName, value ):
    if type(value) == type(()): return value
    if type(value) == type([]): return tuple( value )
    if type(value) == type(''): return tuple( split( value ) )
    raise ValueError, "%s of unsupported type" % valueName


class SimpleHTMLParser(SGMLParser):
    #from htmlentitydefs import entitydefs

    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self.savedata = None
        self.title = ''
        self.metatags = {}
        self.body = ''

    def handle_data(self, data):
        if self.savedata is not None:
            self.savedata = self.savedata + data

    def handle_charref(self, ref):
        self.handle_data("&#%s;" % ref)

    def handle_entityref(self, ref):
        self.handle_data("&%s;" % ref)

    def save_bgn(self):
        self.savedata = ''

    def save_end(self):
        data = self.savedata
        self.savedata = None
        return data

        
    def start_title(self, attrs):
        self.save_bgn()

    def end_title(self):
        self.title = self.save_end()

    def do_meta(self, attrs):
        name = ''
        content = ''
        for attrname, value in attrs:
            value = strip(value)
            if attrname == "name": name = capitalize(value)
            if attrname == "content": content = value
        if name:
            self.metatags[name] = content
    
    def unknown_startag(self, tag, attrs):
        self.setliteral()

    def unknown_endtag(self, tag):
        self.setliteral()
    

bodyfinder = re.compile(r'<body.*?>(?P<bodycontent>.*?)</body>',
                        re.DOTALL|re.I)
htfinder = re.compile(r'<html', re.DOTALL|re.I)

def html_headcheck(html):
    """ Returns 'true' if document looks HTML-ish enough """
    if not htfinder.search(html):
        return 0
    lines = re.split(r'[\n\r]+?', html)
    for line in lines:
        line = strip(line)
        if not line:
            continue
        elif lower(line[:5]) == '<html':
            return 1
        elif line[:2] not in ('<!', '<?'):
            return 0
