"""
    Utility functions.
"""
from string import split, join, lstrip, lower, strip, capitalize
from sgmllib import SGMLParser
import re
import os
from Globals import package_home
_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

def formatRFC822Headers( headers ):
    """
        Convert the key-value pairs in 'headers' to valid RFC822-style
        headers, including adding leading whitespace to elements which
        contain newlines in order to preserve continuation-line semantics.
    """
    munged = []
    linesplit = re.compile( r'[\n\r]+?' )

    for key, value in headers:

        vallines = linesplit.split( value )
        munged.append( '%s: %s' % ( key, join( vallines, '\r\n  ' ) ) )

    return join( munged, '\r\n' )


def parseHeadersBody( body, headers=None, rc=re.compile(r'\n|\r\n')):
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
    lines = rc.split(body)

    i = 0
    if headers is None:
        headers = {}
    else:
        headers = headers.copy()

    hdrlist = []
    for line in lines:
        if not strip(line):
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


def semi_split(s):
    return map(strip, split(s, ';'))

def comma_split(s):
    return map(strip, split(s, ','))

def seq_strip (seq, stripper=strip):
    if type(seq) == type([]):
        return map ( stripper, seq)
    if type(seq) == type(()):
        #seq1 = list(seq)
        return tuple (map(stripper, seq))
    raise ValueError, "%s of unsupported sequencetype %s" % (seq, type(seq))

def tuplize( valueName, value, splitter=split ):
    if type(value) == type(()): return seq_strip( value )
    if type(value) == type([]): return seq_strip( tuple( value ))
    if type(value) == type(''): return seq_strip( tuple( splitter( value ) ))
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
    

_bodyre = re.compile(r'<body.*?>', re.DOTALL|re.I)
_endbodyre = re.compile(r'</body', re.DOTALL|re.I)

def bodyfinder(text):
    bod = _bodyre.search(text)
    if not bod: return text

    end = _endbodyre.search(text)
    if not end: return text
    else: return text[bod.end():end.start()]

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
        elif line[0] != '<':
            return 0
