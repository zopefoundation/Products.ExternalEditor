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

preexp = re.compile(r'<pre>')
unpreexp = re.compile(r'</pre>')
citedexp = re.compile(r'^\s*>')
# Match group 1 is citation prefix, group 2 is leading whitespace:
cite_prefixexp = re.compile('([\s>]*>)?([\s]*)')

def cited_text(text, rfind=string.rfind, strip=string.strip):
    """Quote text for use in literal citations.

    We prepend '>' to each line, splitting long lines (propagating
    existing citation and leading whitespace) when necessary."""
    # (Over?) elaborate stuff snarfed from my wiki commenting provisions.

    got = []
    for line in string.split(text, '\n'):
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
            splitpoint = max(rfind(line[:78-lenpref], ' '),
                             rfind(line[:78-lenpref], '\t'))
            if not splitpoint or splitpoint == -1:
                if strip(line):
                    got.append((pref % continuation_padding) +
                               line)
                line = ''
            else:
                if strip(line[:splitpoint]):
                    got.append((pref % continuation_padding) +
                               line[:splitpoint])
                line = line[splitpoint+1:]
            if not continuation_padding:
                # Continuation lines are indented more than intial - just
                # enough to line up past, eg, simple bullets.
                continuation_padding = '  '
    return string.join(got, '\n')

def process_comment(comment, strip=string.strip):
    """Return formatted comment, escaping cited text."""
    # More elaborate stuff snarfed from my wiki commenting provisions.
    # Process the comment:
    # - Strip leading whitespace,
    # - indent every line so it's contained as part of the prefix
    #   definition list, and
    # - cause all cited text to be preformatted.

    inpre = incited = atcited = 0
    presearch = preexp.search
    presplit = preexp.split
    unpresearch = unpreexp.search
    unpresplit = unpreexp.split
    citedsearch = citedexp.search
    got = []
    for i in string.split(string.strip(comment), '\n') + ['']:
        atcited = citedsearch(i)
        if not atcited:
            if incited:
                # Departing cited section.
                incited = 0
                if inpre:
                    # Close <pre> that we prepended.
                    got.append(' </pre>')
                    inpre = 0

            # Check line for toggling of inpre.
            # XXX We don't deal well with way imbalanced pres on a
            # single line.  Feh, we're working too hard, already.
            if not inpre:
                x = presplit(i)
                if len(x) > 1 and not unprexpsearch(x[-1]):
                    # The line has a <pre> without subsequent </pre>
                    inpre = 1
            else:                   # in <pre>
                x = unpresplit(i)
                if len(x) > 1 and not prexpsearch(x[-1]):
                    # The line has a </pre> without subsequent <pre>
                    inpre = 0

        else:
            # Quote the minimal set of chars, to reduce raw text
            # ugliness. Do the '&' *before* any others that include '&'s!
            if '&' in i and ';' in i: i = string.replace(i, '&', '&amp;')
            if '<' in i: i = string.replace(i, '<', '&lt;')
            if not incited:
                incited = 1
                if not inpre:
                    got.append(' <pre>')
                    inpre = 1
        got.append(' ' + i)
    return string.join(got, '\n')

def add_local_role(object, userid, roleid):
    """Add object roleid for userid if not already there."""
    roles = list(object.get_local_roles_for_userid(userid))
    if roleid not in roles:
        roles.append(roleid)
        object.manage_setLocalRoles(userid, roles)

def get_email_fullname(self, userid):
    """Get full_name or userid, and email, from membership tool."""
    mbrtool = getToolByName(self, 'portal_membership')
    user = mbrtool.getMemberById(userid)
    if user is not None:
        email = None
        name = userid
        try: 
            email = user.email
            name = email.full_name
        except AttributeError:
            pass
        if email:
            if '.' in name or ',' in name:
                name = '"%s"' % name
            return (name or userid, email)
    return (None, None)
