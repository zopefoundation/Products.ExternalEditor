"""
    Utility functions.
"""
from sgmllib import SGMLParser
import re
import os

from Globals import package_home
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo( 'Products.CMFDefault.utils' )

security.declarePrivate('_dtmldir')
_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

security.declarePublic('formatRFC822Headers')
def formatRFC822Headers( headers ):

    """ Convert the key-value pairs in 'headers' to valid RFC822-style
        headers, including adding leading whitespace to elements which
        contain newlines in order to preserve continuation-line semantics.
    """
    munged = []
    linesplit = re.compile( r'[\n\r]+?' )

    for key, value in headers:

        vallines = linesplit.split( value )
        munged.append( '%s: %s' % ( key, '\r\n  '.join( vallines ) ) )

    return '\r\n'.join( munged )


security.declarePublic('parseHeadersBody')
def parseHeadersBody( body, headers=None, rc=re.compile( r'\n|\r\n' ) ):

    """ Parse any leading 'RFC-822'-ish headers from an uploaded
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

        if not line.strip():
            break

        tokens = line.split( ': ' )

        if len( tokens ) > 1:
            hdrlist.append( ( tokens[0], ': '.join( tokens[1:] ) ) )
        elif i == 0:
            return headers, body     # no headers, just return those passed in.
        else:    # continuation
            last, hdrlist = hdrlist[ -1 ], hdrlist[ :-1 ]
            hdrlist.append( ( last[ 0 ]
                            , '\n'.join( ( last[1], line.lstrip() ) )
                            ) )
        i = i + 1

    for hdr in hdrlist:
        headers[ hdr[0] ] = hdr[ 1 ]

    return headers, '\n'.join( lines[ i+1: ] )


security.declarePublic('semi_split')
def semi_split(s):

    """ Split 's' on semicolons.
    """
    return map(lambda x: x.strip(), s.split( ';' ) )

security.declarePublic('comma_split')
def comma_split(s):

    """ Split 's' on commas.
    """
    return map(lambda x: x.strip(), s.split( ',') )

security.declarePublic('seq_strip')
def seq_strip(seq, stripper=lambda x: x.strip() ):

    """ Strip a sequence of strings.
    """
    if type( seq ) == type( [] ):
        return map( stripper, seq )

    if type( seq ) == type( () ):
        return tuple( map( stripper, seq ) )

    raise ValueError, "%s of unsupported sequencetype %s" % ( seq, type( seq ) )

security.declarePublic('tuplize')
def tuplize( valueName, value, splitter=lambda x: x.strip() ):

    if type( value ) == type( () ):
        return seq_strip( value )

    if type( value ) == type( [] ):
        return seq_strip( tuple( value ) )

    if type( value ) == type( '' ):
        return seq_strip( tuple( splitter( value ) ) )

    raise ValueError, "%s of unsupported type" % valueName


class SimpleHTMLParser( SGMLParser ):

    #from htmlentitydefs import entitydefs

    def __init__( self, verbose=0 ):

        SGMLParser.__init__( self, verbose )
        self.savedata = None
        self.title = ''
        self.metatags = {}
        self.body = ''

    def handle_data( self, data ):

        if self.savedata is not None:
            self.savedata = self.savedata + data

    def handle_charref( self, ref ):

        self.handle_data( "&#%s;" % ref )

    def handle_entityref( self, ref ):

        self.handle_data( "&%s;" % ref )

    def save_bgn( self ):

        self.savedata = ''

    def save_end( self ):

        data = self.savedata
        self.savedata = None
        return data

    def start_title( self, attrs ):

        self.save_bgn()

    def end_title( self ):

        self.title = self.save_end()

    def do_meta( self, attrs ):

        name = ''
        content = ''

        for attrname, value in attrs:

            value = value.strip()

            if attrname == "name":
                name = value.capitalize()

            if attrname == "content":
                content = value

        if name:
            self.metatags[ name ] = content
    
    def unknown_startag( self, tag, attrs ):

        self.setliteral()

    def unknown_endtag( self, tag ):

        self.setliteral()

#
#   HTML cleaning code
#

# These are the HTML tags that we will leave intact
VALID_TAGS = { 'a'          : 1
             , 'b'          : 1
             , 'base'       : 1
             , 'blockquote' : 1
             , 'body'       : 1
             , 'br'         : 1
             , 'caption'    : 1
             , 'cite'       : 1
             , 'code'       : 1
             , 'div'        : 1
             , 'dl'         : 1
             , 'dt'         : 1
             , 'dd'         : 1
             , 'em'         : 1
             , 'h1'         : 1
             , 'h2'         : 1
             , 'h3'         : 1
             , 'h4'         : 1
             , 'h5'         : 1
             , 'h6'         : 1
             , 'head'       : 1
             , 'hr'         : 1
             , 'html'       : 1
             , 'i'          : 1
             , 'img'        : 1
             , 'kbd'        : 1
             , 'li'         : 1
           # , 'link'       : 1 type="script" hoses us
             , 'meta'       : 1
             , 'ol'         : 1
             , 'p'          : 1
             , 'pre'        : 1
             , 'span'       : 1
             , 'strong'     : 1
             , 'table'      : 1
             , 'tbody'      : 1
             , 'td'         : 1
             , 'th'         : 1
             , 'title'      : 1
             , 'tr'         : 1
             , 'tt'         : 1
             , 'ul'         : 1
             }

NASTY_TAGS = { 'script'     : 1
             , 'object'     : 1
             , 'embed'      : 1
             , 'applet'     : 1
             }

class IllegalHTML( ValueError ):
    pass

class StrippingParser( SGMLParser ):

    """ Pass only allowed tags;  raise exception for known-bad.
    """

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__( self ):

        SGMLParser.__init__( self )
        self.result = ""

    def handle_data( self, data ):

        if data:
            self.result = self.result + data

    def handle_charref( self, name ):

        self.result = "%s&#%s;" % ( self.result, name )

    def handle_entityref(self, name):

        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):

        """ Delete all tags except for legal ones.
        """
        if VALID_TAGS.get( tag ):

            self.result = self.result + '<' + tag

            for k, v in attrs:

                if k.lower().startswith( 'on' ):
                    raise IllegalHTML, 'Javascipt event "%s" not allowed.' % k

                if v.lower().startswith( 'javascript:' ):
                    raise IllegalHTML, 'Javascipt URI "%s" not allowed.' % v

                self.result = '%s %s="%s"' % (self.result, k, v)

            endTag = '</%s>' % tag
            self.result = self.result + '>'

        elif NASTY_TAGS.get( tag ):
            raise IllegalHTML, 'Dynamic tag "%s" not allowed.' % tag

        else:
            pass    # omit tag

    def unknown_endtag(self, tag):

        if VALID_TAGS.get( tag ):

            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag

security.declarePublic('scrubHTML')
def scrubHTML( html ):

    """ Strip illegal HTML tags from string text.
    """
    parser = StrippingParser()
    parser.feed( html )
    parser.close()
    return parser.result

security.declarePublic('isHTMLSafe')
def isHTMLSafe( html ):

    """ Would current HTML be permitted to be saved?
    """
    try:
        scrubHTML( html )
    except IllegalHTML:
        return 0
    else:
        return 1

security.declarePrivate('_bodyre')
_bodyre = re.compile( r'^\s*<html.*<body.*?>', re.DOTALL | re.I )

security.declarePrivate('_endbodyre')
_endbodyre = re.compile( r'</body', re.DOTALL | re.I )

security.declarePublic('bodyfinder')
def bodyfinder( text ):

    bod = _bodyre.search( text )
    if not bod:
        return text

    end = _endbodyre.search( text )
    if not end:
        return text
    else:
        return text[bod.end():end.start()]

security.declarePrivate('_htfinder')
_htfinder = re.compile( r'<html', re.DOTALL | re.I )

security.declarePublic('html_headcheck')
def html_headcheck( html ):

    """ Return 'true' if document looks HTML-ish enough.
    """
    if not _htfinder.search(html):
        return 0

    lines = re.split(r'[\n\r]+?', html)

    for line in lines:
        line = line.strip()

        if not line:
            continue
        elif line.lower().startswith( '<html' ):
            return 1
        elif line[0] != '<':
            return 0
