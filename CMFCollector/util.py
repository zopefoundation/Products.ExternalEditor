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

"""Sundry collector utilities."""

import string, re
from Products.CMFCore.utils import getToolByName
from DocumentTemplate.DT_Var import html_quote

def users_for_local_role(object, userids, role):
    """Give only designated userids specified local role.

    Return 1 iff any role changes happened."""
    already = []
    changed = 0
    for u in object.users_with_local_role(role):
        if u in userids:
            already.append(u)
        else:
            changed = 1
            remove_local_role(object, u, role)
    for u in userids:
        if u not in already:
            changed = 1
            add_local_role(object, u, role)
    return changed

def add_local_role(object, userid, role):
    """Add object role for userid if not already there."""
    roles = list(object.get_local_roles_for_userid(userid))
    if role not in roles:
        roles.append(role)
        object.manage_setLocalRoles(userid, roles)

def remove_local_role(object, userid, role):
    """Add object role for userid if not already there."""
    roles = list(object.get_local_roles_for_userid(userid))
    roles.remove(role)
    if roles:
        object.manage_setLocalRoles(userid, roles)
    else:
        object.manage_delLocalRoles([userid])

def get_email_fullname(self, userid):
    """Get full_name or userid, and email, from membership tool."""
    mbrtool = getToolByName(self, 'portal_membership')
    user = mbrtool.getMemberById(userid)
    if user is not None:
        if not user.hasProperty('email'):
            return (None, None)         # Not worth bothering.
        email = None
        name = userid
        email = user.getProperty('email')
        name = ((user.hasProperty('full_name') 
                 and user.getProperty('full_name'))
                or str(user))
        if '.' in name or ',' in name:
            name = '"%s"' % name
        return (name, email)
    return (None, None)

def safeGetProperty(userobj, property, default=None):
    """Defaulting user.getProperty(), allowing for variant user folders."""
    try:
        return userobj.getProperty(property, default)
    except TypeError:
        try:
            # Some (eg, our LDAP user folder) support getProperty but not
            # defaulting:
            return userobj.getProperty(property)
        except:
            return default
    except AttributeError:
        # Some don't support getProperty:
        return getattr(userobj, property, default)

##############################
# WebText processing utilities
preexp = re.compile(r'&lt;pre&gt;')
unpreexp = re.compile(r'&lt;/pre&gt;')
urlchars  = (r'[A-Za-z0-9/:@_%~#=&\.\-\?]+')
nonpuncurlchars  = (r'[A-Za-z0-9/@_%~#=&\-]')
url       = (r'["=]?((http|https|ftp|mailto|file|about):%s%s)'
             % (urlchars, nonpuncurlchars))
urlexp=re.compile(url)

def format_webtext(text,
                   presearch=preexp.search, presplit=preexp.split,
                   unpresearch=unpreexp.search, unpresplit=unpreexp.split,
                   urlexpsub=urlexp.sub):
    """Transform web text for browser presentation.

    - HTML quote everything
    - Terminate all lines with <br>s.
    - Whitespace-quote indented and '>' cited lines
    - Whitespace-quote lines within <pre>/</pre> pairs
    - Turn URLs recognized outside of literal regions into links."""

    # Definitions:
    #
    # - "in_literal" exemptions: Lines starting with whitespace or '>'
    # - "in_pre" exemptions: Lines residing within (non-exempted) <pre> tag
    #
    # Nuances:
    #
    # - Neither exemption can toggle while the other applies - each renders
    #   the cues for the other mostly ineffective, except...
    # - in_pre cannot deactivate on a literal-exemption qualifying line, so
    #   pre tags can be used to contain cited text with (ineffective) </pre>s.
    # - We mostly don't handle pre tag nesting, except balanced within a line

    in_pre = at_literal = 0
    got = []
    for l in text.split('\n'):

        if not l:
            got.append(l)
            continue

        l = l.expandtabs()

        at_literal = (l.startswith(" ") or l.startswith("&gt;"))

        if at_literal:
            # Can't open or close <pre> in literal - since it's cited/escaped.
            got.append(l.replace(" ", "&nbsp;"))
                       
        elif in_pre:
            got.append(l.replace(" ", "&nbsp;"))
            # Check for closing pre:
            x = unpresplit(l)
            if len(x) > 1 and not presearch(x[-1]):
                in_pre = 0

        else:
            # Non-literal:
            got.append(urlexpsub(r'<a href="\1">\1</a>', l))
            # Check for opening pre:
            x = presplit(l)
            if len(x) > 1 and not unpresearch(x[-1]):
                # The line has a prevailing <pre>.
                in_pre = 1
            
    return "<br>\n".join(got)

# Match group 1 is citation prefix, group 2 is leading whitespace:
cite_prefixexp = re.compile('([\s>]*>)?([\s]*)')

def cited_text(text, cite_prefixexp=cite_prefixexp):
    """Quote text for use in literal citations.

    We prepend '>' to each line, splitting long lines (propagating
    existing citation and leading whitespace) when necessary."""
    # Over elaborate stuff snarfed from my wiki commenting provisions.

    got = []
    for line in text.split('\n'):
        pref = '> '
        if len(line) < 79:
            got.append(pref + line)
            continue
        m = cite_prefixexp.match(line)
        if m is None:
            pref = '> %s'
        else:
            if m.group(1):
                pref = pref + m.group(1)
                line = line[m.end(1)+1:]
                if m.end(1) > 60:
                    # Too deep quoting - collapse it:
                    pref = '> >> '
                    lencut = 0
            pref = pref + '%s'
            leading_space = m.group(2)
            if leading_space:
                pref = pref + leading_space
                line = line[len(leading_space):]
        lenpref = len(pref)
        continuation_padding = ''
        lastcurlen = 0
        while 1:
            curlen = len(line) + lenpref
            if curlen < 79 or (lastcurlen and lastcurlen <= curlen):
                # Small enough - we're done - or not shrinking - bail out
                if line: got.append((pref % continuation_padding) + line)
                break
            else:
                lastcurlen = curlen
            splitpoint = max(line[:78-lenpref].rfind(' '),
                             line[:78-lenpref].rfind('\t'))
            if not splitpoint or splitpoint == -1:
                if line.strip():
                    got.append((pref % continuation_padding) +
                               line)
                line = ''
            else:
                if line[:splitpoint].strip():
                    got.append((pref % continuation_padding) +
                               line[:splitpoint])
                line = line[splitpoint+1:]
            if not continuation_padding:
                # Continuation lines are indented more than intial - just
                # enough to line up past, eg, simple bullets.
                continuation_padding = '  '
    return string.join(got, '\n')

def sorted(l):
    x = list(l[:])
    x.sort()
    return x
