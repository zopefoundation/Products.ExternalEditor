import re

#international (latin?) characters
intl_char_entities = (
    ('\300', '&Agrave;'),     #À#<--char
    ('\302', '&Acirc;'),      #Â#
    ('\311', '&Eacute;'),     #É#
    ('\312', '&Ecirc;'),      #Ê#
    ('\316', '&Icirc;'),      #Î#
    ('\324', '&Ocirc;'),      #Ô#
    ('\333', '&Ucirc;'),      #Û#
    ('\340', '&agrave;'),     #à#
    ('\342', '&acirc;'),      #â#
    ('\347', '&ccedil;'),     #ç#
    ('\350', '&egrave;'),     #è#
    ('\351', '&eacute;'),     #é#
    ('\352', '&ecirc;'),      #ê#
    ('\356', '&icirc;'),      #î#
    ('\364', '&ocirc;'),      #ô#
    ('\371', '&ugrave;'),     #ù#
    ('\373', '&ucirc;'),      #û#
)
urlchars          = (r'[A-Za-z0-9/:@_%~#=&\.\-\?]+')
url               = (r'["=]?((http|https|ftp|mailto|file|about):%s)'
                     % (urlchars))
urlexp            = re.compile(url)
# trying to co-exist with stx references:
bracketedexpr     = r'\[([^\]0-9][^]]*)\]'
bracketedexprexp  = re.compile(bracketedexpr)
underlinedexpr    = r'_([^_]+)_'
underlinedexprexp = re.compile(underlinedexpr)
wikiname1         = r'\b[A-Z]+[a-z~]+[A-Z0-9][A-Z0-9a-z~]*'
wikiname2         = r'\b[A-Z][A-Z0-9]+[a-z~][A-Z0-9a-z~]*'
simplewikilinkexp = re.compile(r'!?(%s|%s)' % (wikiname1, wikiname2))

wikiending        = r"[ \t\n\r\f\v:;.,<)!?']"
urllinkending     = r'[^A-Za-z0-9/:@_%~\.\-\?]'
wikilink          = (r'!?(%s%s|%s%s|%s|%s%s)'
                    % (wikiname1,wikiending,
                       wikiname2,wikiending,
                       bracketedexpr,url,urllinkending))
wikilinkexp       = re.compile(wikilink)
wikilink_         = r'!?(%s|%s|%s|%s)' % \
                     (wikiname1,wikiname2,bracketedexpr,url)
interwikilinkexp  = re.compile(r'!?((?P<local>%s):(?P<remote>[\w]+))'
                              % (wikilink_))
remotewikiurlexp  = re.compile(r'(?m)RemoteWikiURL[:\s]*(.*)$')
protected_lineexp = re.compile(r'(?m)^!(.*)$')

antidecaptext     = '<!--antidecapitationkludge-->\n'
antidecapexp      = re.compile(antidecaptext)

commentsdelim = "<hr solid id=comments_below>"
preexp = re.compile(r'<pre>')
unpreexp = re.compile(r'</pre>')
citedexp = re.compile(r'^\s*>')
# Match group 1 is citation prefix, group 2 is leading whitespace:
cite_prefixexp = re.compile('([\s>]*>)?([\s]*)')
