"""
The code in this module is available under the GPL.
All rights reserved, all disclaimers apply, etc.

\(c) 1999,2000 Simon Michael <simon@joyful.com>
Parenting code and regulations by Ken Manheimer (klm@digicool.com)
Integrated into Zope CMF by Chris McDonough (chrism@digicool.com)
"""
__version__="$Revision$"[11:-2]

from types import *
import string, re, os
from Globals import HTMLFile, default__class_init__, package_home
from OFS.DTMLDocument import DTMLDocument
from OFS.Image import cookId
from urllib import quote, unquote     # url quoting
from StructuredText import html_with_references #, html_quote
from DocumentTemplate.DT_Var import html_quote
from wwml import translate_WMML
from string import split,join,find,lstrip,lower
import Acquisition
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permission import Permission
from Persistence import Persistent
from DateTime import DateTime
from struct import pack, unpack
from ZWikiRegexes import urlchars, url, urlexp, bracketedexpr,\
     bracketedexprexp, underlinedexpr, underlinedexprexp, wikiname1,\
     wikiname2, simplewikilinkexp, wikiending, urllinkending, wikilink,\
     wikilinkexp, wikilink_, interwikilinkexp, remotewikiurlexp,\
     protected_lineexp, antidecaptext, antidecapexp, commentsdelim,\
     preexp, unpreexp, citedexp, cite_prefixexp, intl_char_entities
import CMFWikiPermissions
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import _getViewFor
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products import CMFDefault
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
DISABLE_JAVASCRIPT = 1

class CMFWikiPage(DTMLDocument, PortalContent, DefaultDublinCoreImpl):
    """ A CMFWiki page """
    portal_type = meta_type = 'CMF Wiki Page'
    page_type = 'structuredtext'
    dtml_allowed = 0
    username=''
    last_editor = None
    _last_safety_belt = ''
    _last_safety_belt_editor = ''
    _safety_belt = None
    last_log = ''
    comment_number = 0
    _st_data = None
    security = ClassSecurityInfo()
    _subowner = 'both'
    SUBOWNER_TYPES = ['creator', 'original_owner', 'both']

    ZWIKI_PAGE_TYPES = [ 'structuredtext'
                       , 'plaintext'
                       , 'html'
                       , 'classicwiki'
                       ]
    # mapping of action category (used by forms) to permission name
    _perms = {
        'move':CMFWikiPermissions.Move,
        'edit':CMFWikiPermissions.Edit,
        'comment':CMFWikiPermissions.Comment,
        'create':CMFWikiPermissions.Create,
        'regulate':CMFWikiPermissions.Regulate
        }
    # mapping of mnemonic pseudorole name (used by forms) to actual role name
    _roles_map = {
        'everyone': ('Anonymous', 'Authenticated'),
        'anyone': ('Anonymous', 'Authenticated'),
        'nonanon': ('Authenticated',),
        'owners':('Owner',),
        }
    # _roles_map backwards
    _reverse_roles_map = {
        'Anonymous': ['everyone', 'anyone'],
        'Authenticated': ['nonanon'],
        'Owner': ['owners'],
        }
    # mapping of action category (used by forms) to local role name
    _local_roles_map = {
        'create': 'CMFWiki Page Creator',
        'edit':'CMFWiki Page Editor',
        'comment':'CMFWiki Page Commentor',
        'move':'CMFWiki Page Mover',
        'regulate':'CMFWiki Page Regulator'
        }
    _properties=({'id':'title', 'type': 'string', 'mode':'w'},
                 {'id':'page_type', 'type': 'selection', 'mode': 'w',
                  'select_variable': 'ZWIKI_PAGE_TYPES'},
                 {'id':'username', 'type': 'string', 'mode': 'w'},
                 {'id':'parents', 'type': 'lines', 'mode': 'w'},
                 {'id':'last_editor', 'type': 'string', 'mode': 'w'},
                 {'id':'last_log', 'type': 'string', 'mode': 'w'},
                 {'id':'comment_number', 'type': 'int', 'mode': 'w'},
                 {'id':'_subowner', 'mode': 'w', 'type': 'selection',
                  'select_variable': 'SUBOWNER_TYPES'},
                 )
    # permission defaults
    set = security.setPermissionDefault
    set(CMFWikiPermissions.Edit, ('Owner', 'Manager', 'Authenticated'))
    set(CMFWikiPermissions.FTPRead, ('Owner', 'Manager'))
    set(CMFWikiPermissions.Regulate, ('Owner', 'Manager'))
    set(CMFWikiPermissions.Create, ('Owner', 'Manager', 'Authenticated'))
    set(CMFWikiPermissions.Move, ('Owner', 'Manager'))
    set(CMFWikiPermissions.Comment, ('Owner', 'Manager', 'Authenticated'))
    set = None

    def __init__(self, __name__='', source_string='', mapping=None):
        DTMLDocument.__init__(self, source_string=source_string,
                              mapping=mapping,
                              __name__=__name__)
        DefaultDublinCoreImpl.__init__(self)

    security.declarePublic('getId')
    def getId(self):
        try: return self.id()
        except TypeError: return self.id

    security.declareProtected(CMFWikiPermissions.View, 'SearchableText')
    def SearchableText(self):
        return self.raw

    security.declareProtected(CMFWikiPermissions.View, '__call__')
    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        '''
        Invokes the default view.
        '''
        view = _getViewFor( self )
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, REQUEST))
        else:
            if REQUEST:
                kw[ 'REQUEST' ] = REQUEST
            if RESPONSE:
                kw[ 'RESPONSE' ] = RESPONSE

            return apply( view, (self,), kw )

    index_html = None  # This special value informs ZPublisher to use __call__

    def render_structuredtext(self, client=None, REQUEST={},
                              RESPONSE=None, **kw):
        # structured text + wiki links + HTML
        t = str(self.xread())
        t = protected_lineexp.sub(self._protect_line, t)
	if self._st_data is None:
            # XXX klm: Shouldn't happen -_st_data should've been set by edit.
            t = str(html_with_references(t, level=3))
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = wikilinkexp.sub(
            thunk_substituter(self._wikilink_replace, t,
                              self.isAllowed('create')),
            t)
        return t

    #XXX this should be structuredtext and the above should be
    #    structuredtexthtml 
    def render_structuredtextonly(self, client=None, REQUEST={},
                              RESPONSE=None, **kw):
        # structured text + wiki links

        t = html_quote(self.xread())
        t = re.sub(protected_line, self._protect_line, t)
	if self._st_data is None:
            # XXX klm: Shouldn't happen -_st_data should've been set by edit.
	   t = str(html_with_references(t, level=3))
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = wikilinkexp.sub(
            thunk_substituter(self._wikilink_replace, t,
                              self.isAllowed('create')),
            t)
        return t


    def render_html(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        # wiki links + HTML
        t = str(self.xread())
        t = protected_lineexp.sub(self._protect_line, t)
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = wikilinkexp.sub(
            thunk_substituter(self._wikilink_replace, t,
                              self.isAllowed('create')),
            t)
        return t

    def render_classicwiki(self, client=None,
                           REQUEST={}, RESPONSE=None, **kw):
        # classic wiki formatting + (inter)wiki links
        t = html_quote(self.xread())
        t = translate_WMML(t)
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = simplewikilinkexp.sub(
            thunk_substituter(self._simplewikilink_replace, t,
                              self.isAllowed('create')), t)
        return t

    def render_plaintext(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        # fixed-width plain text with no surprises
        t = "<pre>\n" + html_quote(self.xread()) + "\n</pre>\n"
        return t

    RENDERERS = { 'structuredtext'      : render_structuredtext
                , 'structuredtextonly'  : render_structuredtextonly
                , 'html'                : render_html
                , 'classicwiki'         : render_classicwiki
                , 'plaintext'           : render_plaintext
                }

    def render( self, client=None, REQUEST={}, RESPONSE=None, **kw ):
        """
            Determine the appropriate renderer, and call it.
        """
        renderer = self.RENDERERS[ self.page_type ]
        if client is None:
            client = self
        return apply( renderer, ( self, client, REQUEST, RESPONSE ), kw )

    # XXX see render_structuredtextdtml
    def xread(self):
        return antidecapexp.sub('', self.read())

    # utility method for wiki-linking an arbitrary text snippet
    # could modify the render_ methods to do this instead
    def wikilink(self, text):
        t = protected_lineexp.sub(self._protect_line, text)
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = wikilinkexp.sub(self._wikilink_replace, t)
        return t

    security.declarePublic('htmlquote')
    def htmlquote(self, text):
        return html_quote(text)

    def _protect_line(self, match):
        """protect an entire line from _wikilink_replace, by
           protecting all its wikilink occurrences
        """
        return wikilinkexp.sub(r'!\1', match.group(1))

    def _my_folder(self):
        """ Obtain parent folder """
        return aq_parent(aq_inner(self))

    def _makeCreationLink( self, wiki_name, allowed ):
        # Build the wiki creation link
        action = self.REQUEST.get( 'WikiCreateAction', None )
        if action is None:
            action = self.getTypeInfo().getActionById( 'create' )
            self.REQUEST.set( 'WikiCreateAction', action )
        fmt =  ( allowed
             and '%s<a href="%s/%s?page=%s">?</a>'
              or '%s<sup><a href="%s/%s?page=%s">x</a></sup>'
               )
        return fmt % ( wiki_name
                     , quote( self.getId() )
                     , action
                     , quote( wiki_name )
                     )


    def _simplewikilink_replace(self, match, allowed=1, state=None, text=''):
        """replace an occurrence of simplewikilink with a suitable hyperlink

        To be used as a re.sub repl function *and* get a proper value for
        literal context, 'allowed', etc, enclose this function with the value
        using 'thunk_substituter'.
        """
        # In a literal?
        if state is not None:
            if within_literal(match.start(1), match.end(1)-1, state, text):
                return match.group(1)

        # matches beginning with ! should be left alone
        if re.match('^!',match.group(0)):
            return match.group(1)

        m = match.group(1)

        folder = self._my_folder()
        # if something of this name exists, link to it;
        # otherwise, provide a "?" creation link
        if hasattr(aq_base(folder), m): 
            # Actually contained within the folder:
            return '<a href="%s">%s</a>' % (quote(m), m)
        elif hasattr(folder, m):
            obj = getattr(folder, m)
            if not hasattr(obj, 'absolute_url'):
                # Whoops!  Probly an acquired method, which we do *not* want
                # want to link, and which we do *not* want to allow being
                # shadowed by a wiki page.
                return '%s<font color="red"><sup>x</sup></font>' % m
            # Obtained by acquisition - make sure to use the real URL:
            return '<a href="%s">%s</a>' % (obj.absolute_url(), m)

        # otherwise, provide a suitable creation link
        else:
            return self._makeCreationLink( m, allowed )

    def _wikilink_replace(self, match, allowed=0, state=None, text=''):
        """Replace occurrence of the wikilink regexp with suitable hyperlink.

        To be used as a re.sub repl function *and* get a proper value for
        literal context, 'allowed', etc, enclose this function with the value
        using 'thunk_substituter'.
        """
        # In a literal?
        if state is not None:
            if within_literal(match.start(1), match.end(1)-1, state, text):
                return match.group(1)

        # matches beginning with ! should be left alone
        mg0 = match.group(0)
        if mg0 and mg0[0] == '!':
            return match.group(1)

        m = match.group(1)
        # Jim's stuff: we have to handle the trailing character
        # specially depending on how we got here.
        e=m[-1:]
        if e == ']': e=''
        else: m=m[:-1]

        # strip any enclosing []'s that were used
        if bracketedexprexp.match(m):
            m = bracketedexprexp.sub(r'\1', m)
        elif underlinedexprexp.match(m):
            m = underlinedexprexp.sub(r'\1', m)
        
        folder = aq_parent(aq_inner(self))
        # if it's an ordinary url, link to it
        if urlexp.match(m):
            # except, if preceded by " or = it should probably be left alone
            if re.match('^["=]',m):                                   # "
                return m+e
            else:
                return ('<a href="%s">%s</a>' % (m, m))+e

        # a wikiname - if page (or something) of this name exists, link to
        # it.
        elif hasattr(aq_base(folder), m):
            # Actually contained wihtin the folder:
            return '<a href="%s">%s</a>' % (quote(m), m) + e
        elif hasattr(folder, m):
            # Obtained by acquisition - make sure to use the real URL:
            obj = getattr(folder, m)
            if not hasattr(obj, 'absolute_url'):
                # Whoops!  Probly an acquired method, to which we do *not*
                # want to link, and which we do *not* want to allow being
                # shadowed by a wiki page.
                return '%s<font color="red"><sup>x</sup></font>' % m + e
            return '<a href="%s">%s</a>' % (obj.absolute_url(), m) + e

        # otherwise, provide a suitable creation link
        else:
            return self._makeCreationLink( m, allowed ) + e

    def _interwikilink_replace(self, match, allowed=0, state=None, text=''):
        """replace an occurrence of interwikilink with a suitable hyperlink.

        To be used as a re.sub repl function *and* get a proper value for
        literal context, 'allowed', etc, enclose this function with the value
        using 'thunk_substituter'.
        """
        # In a literal?
        if state is not None:
            if within_literal(match.start(1), match.end(1)-1, state, text):
                return match.group(1)

        # matches beginning with ! should be left alone
        mg0 = match.group(0)
        if mg0 and mg0[0] == '!': return match.group(1)

        localname  = match.group('local')
        remotename = match.group('remote') # named groups come in handy here!

        # look for a RemoteWikiURL definition
        if hasattr(self._my_folder(), localname): 
            localpage = getattr(self._my_folder(),localname)
            # local page found - search for "RemoteWikiUrl: url"
            m = remotewikiurlexp.search(str(localpage))
            if m is not None:
                remoteurl = html_unquote(m.group(1)) # NB: pages are 
                                                     # stored html-quoted
                                                     # XXX eh ? they are ?
                                                     # something's not
                                                     # right
                                                     # somewhere.. 
                                                     # I have lost my
                                                     # grip on this
                                                     # whole quoting
                                                     # issue.
                
                # we have a valid inter-wiki link
                link = '<a href="%s%s">%s:%s</a>' % \
                       (remoteurl, remotename, localname, remotename)
                # protect it from any later wiki-izing passes
                return wikilinkexp.sub(r'!\1', link)

        # otherwise, leave alone
        return match.group(0)

    security.declareProtected(CMFWikiPermissions.Edit, 'manage_edit')
    def manage_edit(self, data, title, REQUEST=None):
        """Do standard manage_edit kind of stuff,but use our special edit."""
        self.edit(text=data, title=title)
        self.reindexObject()
        if REQUEST:
            message="Content changed."
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    security.declareProtected(CMFWikiPermissions.Move, 'delete')
    def delete(self):
        """ Deletes this page from the folder """
        id = self.getId()
        if id == 'FrontPage':
            raise ValueError, "FrontPage may not be deleted."
        folder = self._my_folder()
        folder._delObject(id)
        self.unindexObject()

    security.declareProtected(CMFWikiPermissions.Move, 'rename')
    def rename(self, new_id):
        """ Renames this page """
        old_id = self.getId()
        if new_id == old_id:
            raise ValueError, ("New name (%s) must be different than old."
                               % new_id)
        folder = self._my_folder()
        if hasattr(aq_base(folder), new_id):
            raise ValueError, ("Page with new name '%s' already exists."
                               % new_id)
        folder._delObject(old_id)
        self.__name__ = new_id
        folder._setObject(new_id, aq_base(self))
        self = getattr(folder, new_id)
        self.unindexObject()
        self.indexObject()
        return self.wiki_page_url()

    security.declareProtected(CMFWikiPermissions.Comment, 'comment')
    def comment(self, comment, ack_requested=None):
        """ Handles comments """
        self.comment_number = self.comment_number + 1
        text = self._st_data or self.xread()
        log = 'Comment #%s' % self.comment_number
        if ack_requested is not None:
            log = '*' + log
        log = string.strip(log)
        get_transaction().note(log)
        self.last_log = log
        user = getSecurityManager().getUser()
        username = user.getUserName()
        if username == 'Anonymous User':
            username = ''
        self.last_editor = username
        self.username = username
        t = text + self._process_comment(comment, text, ack_requested)
        self._set_text(t)
        self.reindexObject()

    security.declareProtected(CMFWikiPermissions.Edit, 'edit')
    def edit(self, text=None, type=None, title='', log=None, timeStamp=None):
        """
        Handles edits.
        
        Usually called from a time-stamped web form; we use timeStamp
        to detect and warn when two people attempt to work on a page
        at the same time.
        """
        # Check for edit conflicts except for comments, which are
        # appended.
        self.checkEditTimeStamp(timeStamp) 
        user = getSecurityManager().getUser()
        username = user.getUserName()
        if username == 'Anonymous User': username = ''
        self.last_editor = username
        if type is not None:
            self.username = username
            self.page_type = type
        if log and string.strip(log):
            log = string.strip(log)
            get_transaction().note(log)
            self.last_log = log
        else:
            self.last_log = None
        self.title=title
        if text is not None:
            self.username = username
            t = text
            self._set_text(t)
        self.reindexObject()
        
    security.declarePublic('page_owners')
    def page_owners(self, limit=None):
        """Return a list of users with Owner role in wiki page."""
        got = []
        for k, v in self.get_local_roles():
            if 'Owner' in v and k not in got:
                got.append(k)
                if limit and len(got) > limit:
                    got.append('...')
                    return got
        return got

    security.declarePublic('isAllowed')
    def isAllowed(self, op, **kw): 
        """ determine if currently logged in user is able to perform
        the operation associated with the string represented by op
        **kw exists in the arglist in case anything still tries to
        pass in REQUEST, it should go away at some point"""
        return getSecurityManager().checkPermission(self._perms[op], self)
    
    security.declareProtected(CMFWikiPermissions.Regulate, 'setSubOwner')
    def setSubOwner(self, which):
        """Set how owner role of pages created from this page is determined.
        Which must be one of:
         - 'creator': person doing the page creation.
         - 'original_owner': parties that have owner role for this page.
         - 'both': includes both 'original_owner' and 'creator'."""
        if which in ('creator', 'original_owner', 'both'):
            self._subowner = which
        else:
            raise ValueError, "Bad subowner value '%s'" % which

    security.declarePublic('subOwner')
    def subOwner(self):
        """Identify who gets ownership of pages created from this page."""
        return self._subowner

    security.declarePublic('isRegSetter')
    def isRegSetter(self):
        """User is among those allowed to set the regulations for curr page.
        """
        check = getSecurityManager().checkPermission
        return check(self._perms['regulate'], self)

    security.declarePrivate('clearLocalWikiRoles')
    def clearLocalWikiRoles(self):
        """ Remove all local role assignments to wiki-related permissions
        respective to this object """
        new_local_roles = {}
        for username, roles in self.get_local_roles():
            roles = list(roles)
            for action in self._local_roles_map.values():
                if action in roles:
                    roles.remove(action)
            new_local_roles[username] = roles
        for username, roles in new_local_roles.items():
            if not roles:
                self.manage_delLocalRoles([username])
            else:
                self.manage_setLocalRoles(username, list(roles))

    security.declareProtected(CMFWikiPermissions.Regulate, 'setOp')
    def setOp(self, op, usernames, category):
        """Set who can do a particular operation."""
        if category is None:
            raise "Programmer error, eviscerate programmer"
        this_perm = self._perms[op]
        these_roles = self._roles_map[category]
        this_local_role = self._local_roles_map[op]
        self.manage_permission(this_perm, these_roles)
        for username in usernames:
            username and \
                     self.manage_addLocalRoles(username,[this_local_role])

    security.declareProtected(CMFWikiPermissions.Regulate, 'setRegulations')
    def setRegulations(self, d):
        """Set regulations for CMFWiki page """
        offspring = None
        # clear local roles related to Wiki stuff
        self.clearLocalWikiRoles()
        for op in self.regOps(): # create, edit, comment, move
            usernames = d.get(op + '-usernames', [])
            category = d.get(op + '-category', None)
            self.setOp(op, usernames, category)
            # Propagate to subpages if desired
            if lower(d.get('propagate-' + op, None)) == "on":
                if offspring is None:
                    page_meta_type = self.meta_type
                    nesting = WikiNesting(self._my_folder(), page_meta_type)
                    offspring = flatten(nesting.get_offspring([self.getId()])
                                        )
                    offspring.remove(self.getId())
                for sub in offspring:
                    subobj = self._my_folder()[sub]
                    if subobj.isRegSetter():
                        subobj.setOp(op, usernames, category)
        d.has_key('who_owns_subs') and self.setSubOwner(d['who_owns_subs'])
        
    security.declarePublic('regOps')
    def regOps(self):
        """ """
        return ('create', 'edit', 'comment', 'move')
    
    security.declarePublic('regCategories')
    def regCategories(self):
        """ """
        return ('nobody', 'owners', 'nonanon', 'everyone')

    security.declarePublic('whichWho')
    def whichWho(self, op):
        category = self.opCategory(op)
        if category == 'nonanon': return 'You must be logged-in to'
        if category == 'owners': return 'Only the owners may'
        if category == 'nobody': return 'Nobody may'
        else: return 'Everyone may'
    
    security.declarePublic('opCategory')
    def opCategory(self, op):
        """Return category setting for specified operation."""
        requested_permission = self._perms[lower(op)]
        roles = []
        for p in self.ac_inherited_permissions(1):
            name, value = p[:2]
            if name == requested_permission:
                p = Permission(name, value, self)
                roles = p.getRoles()
                break
        if 'Anonymous' in roles: return 'everyone'
        elif 'Authenticated' in roles: return 'nonanon'
        elif 'Owner' in roles: return 'owners'
        else: return 'nobody'

    security.declarePublic('opUsernames')
    def opUsernames(self, op):
        """Return localrole usernames with privilege to carry out operation
        op"""
        usernames = {}
        local_roles = self.get_local_roles()
        this_local_role = self._local_roles_map[op]
        for username, roles in local_roles:
            if this_local_role in roles:
                usernames[username] = 1
        return tuple(usernames.keys())

    security.declareProtected(CMFWikiPermissions.Create, 'create_page')
    def create_page(self, page, text='', title='', log=None,
                    page_type='structuredtext'):
        """Create a new page."""
        if hasattr(aq_base(self._my_folder()), page):
            raise ValueError, ("Document with name '%s' already exists.\n"
                               "(Perhaps it was created while you were "
                               "editing.)" % page)
        ob = self.__class__(source_string='', __name__=page)
        initPageMetadata(ob)
        ob.page_type = page_type
        ob.title = str(title)
        ob.parents = [self.getId()]
        folder = self._my_folder()
        id = folder._setObject(page,ob)
        ob = getattr(folder, id)
        # 2.2-specific: the new page object is owned by the current
        # authenticated user, if any; not desirable for executable content.
        # Remove any such ownership so that the page will acquire it's
        # owner from the parent folder.
        ob._deleteOwnershipAfterAdd()

        username = getSecurityManager().getUser().getUserName()
        subowner = self.subOwner()

        owners = {}
        for luser, roles in self.get_local_roles():
            if 'Owner' in roles:
                owners[luser] = 1
        owners = owners.keys()

        # Make Owner local role(s)
        if subowner == 'original_owner':
            for user in owners:
                ob.manage_addLocalRoles(user, ['Owner'])

        elif subowner == 'both':
            ob.manage_addLocalRoles(username, ['Owner'])
            for user in owners:
                ob.manage_addLocalRoles(user, ['Owner'])
                
        else: # creator or unspecified
            ob.manage_addLocalRoles(username, ['Owner'])
                                    
        ob.setSubOwner(subowner)

        # set CRUD permissions against local roles
        # e.g. give Move Wiki Page (perm) -> Wiki Page Movers ([local] role)
        # this effectively allows us to grant or deny a user any of the
        # four "operation" types on a per-page basis.
        # also carry over permissions from parent page.
        for op, permission in ob._perms.items():
            pseudoperm = self.opCategory(op)
            these_roles = self._roles_map[pseudoperm]
            this_local_role = self._local_roles_map[op]
            roles = (this_local_role,) + these_roles
            ob.manage_permission(permission, roles=roles)

        # propagate parent local Wiki roles settings
        for localuser, localroles in self.get_local_roles():
            goodroles = []
            for localrole in localroles:
                if localrole in self._local_roles_map.values():
                    goodroles.append(localrole)
            localuser and goodroles and \
                      ob.manage_addLocalRoles(localuser,goodroles)

        ob._set_text(text)
        if log:
            get_transaction().note(log)
        if username == 'Anonymous User':
            username = ''
        ob.last_editor = username
        ob.indexObject()
        
    # we want a Wiki page's manage_upload method to be
    # protected by something other than 'Change DTML Methods'
    security.declareProtected(CMFWikiPermissions.Edit, 'manage_upload')
    security.declareProtected(CMFWikiPermissions.Create, 'create_file')
    def create_file(self, id, file='', filetype='file', title='',
                    precondition='', content_type=''):
        # Lifted from OFS/Image.py:File:manage_addFile
        """Add a new File or Image object, depending on 'filetype'.

        Creates a new File object 'id' with the contents of 'file'"""
        # Ensure the page still doesn't exist.
        if hasattr(self._my_folder().aq_base, id):
            raise ValueError, ("Document with name '%s' already exists.\n"
                               "(Perhaps it was created while you were "
                               "editing.)" % id)

        id=str(id)
        title=str(title)
        content_type=str(content_type)
        precondition=str(precondition)

        id, title = cookId(id, title, file)

        folder=self._my_folder()

        if string.lower(filetype) == 'image':
            obj = CMFDefault.Image.Image(
                id, title,'', content_type, precondition)
        else:
            obj = CMFDefault.File.File(
                id,title,'', content_type, precondition)
        folder._setObject(id, obj)
        folder._getOb(id).manage_upload(file)

    def _set_text(self, text=''):
        """change the page text, with cleanups and perhaps DTML validation
        """
        t = self._text_cleanups(text)
        # Stash copy of text before structured text processing, and 
        # work onward with processed version:
        self._st_data = t
        if string.find(self.page_type, 'structuredtext') != -1:
            if string.strip(t):
                t = str(html_with_references(t, level=3))
        # for DTML page types, execute the DTML to catch problems -
        # zope will magically roll back this whole transaction and the
        # user will get an appropriate error
        self.raw = t

    def _text_cleanups(self, t):
        """do some cleanup of a page's new text
        """
        # strip any browser-appended ^M's
        t = re.sub('\r\n', '\n', t)

        # convert international characters to HTML entities for safekeeping
        for c,e in intl_char_entities:
            t = re.sub(c, e, t)

        # here's the place to strip out any disallowed html/scripting
        # elements 
        if DISABLE_JAVASCRIPT:
            t = re.sub(r'(?i)<([^d>]*script[^>]*)>',r'<disabled \1>',t)

        return t

    def _process_comment(self, comment, text, ack_requested,
                         preexp=re.compile('<pre>'), strip=string.strip):
        """Return formatted comment, escaping cited text.

        Add an "Editor Remark Requested" ditty if requested.

        We prepend an <HR> delimiter for all comment if there's not one
        already in the text.
        """
        iseditor = self.isAllowed('edit')
        timestamp = DateTime().aCommon()
        userid = getSecurityManager().getUser().getUserName()

        if string.find(text, commentsdelim) == -1:
            # No commentsdelim there yet, prepend one to the current comment.
            got =  ['', '', commentsdelim, '']
        else:
            got =  []
        if ack_requested:
            ack = '*Editor Remark Requested*'
        else:
            ack = ''
        got.append('\n%s (%s; Comment #%s) %s --'
                   % (userid, timestamp, self.comment_number, ack))

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
                else:
                    # we are in <pre>
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

    security.declarePublic('get_page_history')
    def get_page_history(self, mode='condensed',
                         batchsize=30, first=0, last=30):
        """Return history records for a page, culling according to mode
        param.

        'complete': all records.

        'condensed': Omit showing prior versions of page replaced
                     subsequently and soon after by the same person
                     using same (possibly empty) log entry

        Currently 
        """
        r = self._p_jar.db().history(self._p_oid, None, 5000)
        for i in range(len(r)): r[i]['tacked_on_index'] = i

        if mode == 'complete':
            pass
        elif mode == 'condensed':
            # Each entry may:
            #  - either continue an existing session or start a new one, and
            #  - either be a landmark or not.
            got = []
            carrying = None
            prevdescr = None
            # Put in least-recent-first order:
            r.reverse()
            for entry in r:

                curdescr = split(entry['description'], '\012')[1:]

                # Handle prior retained stuff:
                if carrying:
                    if carrying['user_name'] != entry['user_name']:
                        # Different user:
                        got.append(carrying)
                    elif curdescr != prevdescr:
                        # Different log entry:
                        got.append(carrying)
                    else:
                        itime, ctime = entry['time'], carrying['time']
                        if type(itime) == FloatType:
                            itime = entry['time'] = DateTime(itime)
                        if type(ctime) == FloatType:
                            ctime = carrying['time'] = DateTime(ctime)
                        if (float(itime - ctime) * 60 * 24) > 30:
                            # Enough time elapsed:
                            # XXX klm "Enough time" should be configurable...
                            got.append(carrying)

                # Old-session, if any, was handled - move forward:
                carrying = entry
                prevdescr = curdescr

            if carrying:
                # Retain final item
                got.append(carrying)

            # Put back in most-recent-first order:
            got.reverse()
            r = got
        else:
            raise ValueError, "Unknown mode '%s'" % mode

        for d in r:
            if type(d['time']) == FloatType:
                d['time'] = DateTime(d['time'])
            d['key']=join(map(str, unpack(">HHHH", d['serial'])),'.')

        r=r[first:first+batchsize+1]

        return r

    security.declareProtected(CMFWikiPermissions.Edit,
                              'history_copy_page_to_present')
    def history_copy_page_to_present(self, keys=[]):
        """Create a new object copy with the contents of an historic copy."""
        self.manage_historyCopy(keys=keys)
        self.reindexObject()

    security.declareProtected(CMFWikiPermissions.View,
                              'history_compare_versions')
    def history_compare_versions(self, keys=[], REQUEST=None):
        """Do history comparisons.

        Mostly stuff adapted from OFS.History -
        manage_historicalComparison() and manage_historyCompare(),
        with a bit of direct calling of html_diff."""
        from OFS.History import historicalRevision, html_diff
        if not keys:
            raise HistorySelectionError, (
                "No historical revision was selected.<p>")
        if len(keys) > 2:
            raise HistorySelectionError, (
                "Only two historical revision can be compared<p>")
        
        serial=apply(pack, ('>HHHH',)+tuple(map(string.atoi,
                                                split(keys[-1],'.'))))
        rev1=historicalRevision(self, serial)
        
        if len(keys)==2:
            serial=apply(pack,
                         ('>HHHH',)+tuple(map(string.atoi,
                                              split(keys[0],'.'))))

            rev2=historicalRevision(self, serial)
        else:
            rev2=self

        dt1=DateTime(rev1._p_mtime)
        dt2=DateTime(rev2._p_mtime)
        t1, t2 = rev1._st_data, rev2._st_data
        if t1 is None or t2 is None:
            t1, t2 = rev1.xread(), rev2.xread()
        historyComparisonResults = html_diff(t1, t2)
        return dt1, dt2, historyComparisonResults

    def __str__(self):
        return self.quotedHTML(self._st_data or self.xread())

    # jim's safety belts for warning of http & ftp edit conflicts
    security.declareProtected(CMFWikiPermissions.FTPRead, 'manage_FTPget')
    def manage_FTPget(self):
        "Get source for FTP download"

        headers = []
        headers.append( "Wiki-Safetybelt: %s" % self.editTimestamp() )

        parents = self.getParents()
        if type( parents ) is not StringType:
            parents = string.join( parents, ", " )
        headers.append( "Wiki-Parents: %s" % parents )

        candidates = ['structuredtext', 'plaintext']
        types = "%s (alternatives:" % self.page_type
        if self.page_type in candidates:
            candidates.remove(self.page_type)
        for i in candidates:
            types = types + " %s" % i
        types = types + ")"
        headers.append( "Type: %s" % types )
        headers.append( "Log: " )

        return "%s\n\n%s" % ( string.join( headers, "\n" )
                            , self._st_data or self.xread()
                            )

    security.declareProtected(CMFWikiPermissions.Edit, 'PUT')
    def PUT( self
           , REQUEST
           , RESPONSE
           , COMMA_SPACE=re.compile( "[, ]+" )
           ):
        """
            Handle HTTP/FTP/WebDav PUT requests.
        """
        self.dav__init(REQUEST, RESPONSE)
        body=REQUEST.get('BODY', '')
        self._validateProxy(REQUEST)

        headers, body = parseHeadersBody(body)

        # Try 'Log' or 'log'.
        log = string.strip(headers.get('Log',headers.get('log', ''))) or None
        type = (string.strip(headers.get('Type', headers.get('type', '')))
                or None)
        if type is not None:
            type = string.split(type)[0]
            candidates = ['structuredtext', 'plaintext']
            if type not in candidates:
                # Silently ignore it.
                type = None
        timestamp = string.strip(headers.get('Wiki-Safetybelt', '')) or None
        try:
            self.edit(body, type=type, log=log, timeStamp=timestamp)
        except 'EditingConflict':
            get_transaction().abort()
            RESPONSE.setStatus(450)
            return RESPONSE

        NO_PARENTS = []
        new_parents = headers.get( 'Wiki-Parents', NO_PARENTS )

        if new_parents is not NO_PARENTS:

            new_parents = filter( None, COMMA_SPACE.split( new_parents ) )
            new_parents.sort()
            old_parents = list( self.getParents() )
            old_parents.sort()
            if new_parents != old_parents:
                self.reparent( new_parents )

        RESPONSE.setStatus(204)
        return RESPONSE
    
    security.declarePublic('checkEditTimeStamp')
    def checkEditTimeStamp(self, timeStamp=''):
        """Check validity of safety belt and update tracking if valid.

        Return 0 if safety belt is invalid, 1 otherwise.

        Note that the policy is deliberately lax if no safety belt value is
        present - "you're on your own if you don't use your safety belt".

        When present, either the safety belt token:
         - ... is the same as the current one given out, or
         - ... is the same as the last one given out, and the person doing the
               edit is the same as the last editor."""

        this_belt = timeStamp
        this_user = getSecurityManager().getUser().getUserName()

        if (# we have a safety belt value:
            this_belt
            # and the current object has a one (ie - not freshly minted):
            and (self._safety_belt is not None)
            # and the submitted safety belt doesn't match the current one:
            and (this_belt != self._safety_belt)
            # and safety belt + user don't match last safety belt + user:
            and not ((this_belt == self._last_safety_belt)
                     and (this_user == self._last_safety_belt_editor))):
            # Fail.
            raise 'EditingConflict', (
                'Someone has edited this page since you loaded the page '
                'for editing.  Try editing the page again.')

        # We qualified - either:
        #  - the edit was submitted with safety belt stripped, or
        #  - the current safety belt was used, or
        #  - the last one was reused by the last person who did the last edit.
        # In any case, update the tracking.

        self._last_safety_belt_editor = this_user
        self._last_safety_belt = this_belt
        self._safety_belt = str(self._p_mtime)

        return 1

    security.declarePublic('editTimestamp')
    def editTimestamp(self):
        if self._safety_belt is None:
            return str(self._p_mtime)
        return self._safety_belt

    security.declarePublic('getParents')
    def getParents(self):
        return tuple(self.parents)
    
    security.declarePublic('backlinks')
    def backlinks(self, REQUEST=None):
        """
        Return a data structure in the form representing pages linked to
        this page:

        [{'pageid':'foo','isparent': 0},{'pageid':'bar','isparent':1}, ...]
        """
        backlinks = []
        folder = self._my_folder()
        myparents = self.getParents()
        names = folder.objectIds(spec=self.meta_type)
        for name in names:
            ob = getattr(folder, name)
            if find(ob.raw, self.getId()) != -1:
                pageid = ob.getId()
                if pageid in myparents:
                    backlinks.append({'pageid':pageid, 'isparent':1})
                else:
                    backlinks.append({'pageid':pageid, 'isparent':0})
        return backlinks
    
    security.declareProtected(CMFWikiPermissions.View, 'text')
    def text(self, REQUEST=None, RESPONSE=None):
        """ document source """
        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/plain')
        return self._st_data or self.read()

    security.declarePublic('wiki_page_url')
    def wiki_page_url(self):
        """return the url path for the current wiki page"""
        return '/' + self.absolute_url(relative=1)

    security.declarePublic('wiki_base_url')
    def wiki_base_url(self):
        """return the base url path for the current wiki"""
        return '/' + self._my_folder().absolute_url(relative=1)

    security.declareProtected(CMFWikiPermissions.Move, 'reparent')
    def reparent(self, parents=None):
        """Reset parents property according to request."""
        if parents is None:
            self.parents = []
        else:
            if type(parents) != ListType:
                if type(parents) != StringType:
                    raise "Parents must be list or string"
                parents = [parents]
            self.parents = parents

    security.declarePublic('get_ancestors')
    def get_ancestors(self):
        """Return trimmed nesting structure indicating this page's ancestors.

        See the WikiNesting docstring for nestings structure description."""
        container = self._my_folder()
        allpages = container.objectIds(spec=self.meta_type)
        ancestors = {}
        offspring = {}
        tops = {}                       # Ancestors that have no parents.
        todo = {self.getId(): None}
        while todo:
            doing = todo
            todo = {}
            for i in doing.keys():
                if ancestors.has_key(i):
                    continue            # We've already collected this one.
                else:
                    if not hasattr(container, i):
                        continue        # Absent - ignore it.
                    ancestors[i] = None
                    obj = container[i]
                    if not hasattr(obj, 'parents'):
                        continue
                    parents = obj.parents
                    if type(parents) != ListType: # SKWM
                        parents = []
                    if parents:
                        defunct = []
                        for p in parents:
                            if p in defunct: continue
                            elif p not in allpages:
                                defunct.append(p)
                                continue
                            if offspring.has_key(p):
                                offspring[p].append(i)
                            else:
                                offspring[p] = [i]
                            todo[p] = None
                        if len(defunct) == len(parents):
                            # None of the parents exist - we have an orphan.
                            tops[i] = None
                    else: tops[i] = None

        # Ok, now go back down, unravelling each forebear only once:
        tops = tops.keys()
        tops.sort
        did = {}; got = []
        for t in tops:
            got.append(descend_ancestors(t, ancestors, did, offspring))
        return got or [[self.getId()]]

    security.declarePrivate('listActions')
    def listActions( self, info ):
        return [ { 'name' : 'Help'
                 , 'url' : "javascript:window.open("
                         "'WikiHelp',"
                         "'WikiHelp',"
                         "'menubar=no,toolbar=yes,"
                         "scrollbars=yes,resizable=yes,"
                         "height=300,width=500"
                           "').focus();"
                 , 'permissions' : []
                 , 'category' : 'object'
                 } ]
        
    security.declarePublic('wiki_context')
    def wiki_context(self, REQUEST=None, with_siblings=0):
        """Return HTML showing this page's parents and siblings."""
        myid = self.getId()
        if with_siblings:
            page_meta_type = self.meta_type
            nesting = WikiNesting(self._my_folder(), page_meta_type)
            nesting = nesting.get_up_and_back(myid)
        else:
            nesting = self.get_ancestors()
        return present_nesting(myid,nesting,self._my_folder().absolute_url(),
                               no_anchors=1)

    security.declarePublic('offspring')
    def offspring(self, REQUEST=None):
        """Return a presentation of all my offspring."""
        myid = self.getId()
        page_meta_type = self.meta_type
        nesting = WikiNesting(self._my_folder(), page_meta_type)
        return present_nesting(myid, nesting.get_offspring([myid]),
                               self.wiki_base_url()) # SKWM

    security.declarePublic('wiki_map')
    def wiki_map(self, REQUEST=None):
        """Present the nesting layout of the entire wiki, showing:
        - All the independent nodes, ie those without parents or children,
        - All the branches in the wiki - from the possibly multiple roots."""
        map = WikiNesting(self._my_folder(), self.meta_type).get_map()
        singletons = []
        combos = []
        for i in map:
            if type(i) == StringType:
                singletons.append(i)
            else:
                combos.append(i)
        nesting = present_nesting(self.getId(), combos, self.wiki_base_url())
        return nesting, singletons

    security.declarePublic('Title')
    def Title(self): # for CMFCatalog
        return self.title_or_id()
    
    security.declarePublic('title_or_id')
    def title_or_id(self):
        if self.title:
            return self.title
        fid = self._my_folder().getId()
        return "%s of %s" % (self.getId(), fid)
    
    def __repr__(self):
        return ("<%s %s at 0x%s>" % (self.__class__.__name__, `self.getId()`,
                                     hex(id(self))[2:])
                )
    security.declarePublic('prep_citation')
    def prep_citation(self, rfind=string.rfind, strip=string.strip):
        """Quote text for use in literal citations.

        We prepend '>' to each line, splitting long lines (propagating
        existing citation and leading whitespace) when necessary."""
        got = []
        for line in string.split(self._st_data or self.xread(), '\n'):
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

def thunk_substituter(func, text, allowed):
    """Return a function which takes one arg and passes it with other args
    to passed-in func.

    thunk_substituter passes in the value of it's parameter, 'allowed', and a
    dictionary {'lastend': int, 'inpre': bool, 'intag': bool}.

    This is for use in a re.sub situation, to get the 'allowed' parameter and
    the state dict into the callback.

    (The technical term really is "thunk".  Honest.-)"""
    state = {'lastend': 0, 'inpre': 0, 'incode': 0, 'intag': 0}
    return lambda arg, func=func, allowed=allowed, text=text, state=state: (
        func(arg, allowed, state, text))

def within_literal(upto, after, state, text,
                   rfind=string.rfind, lower=string.lower):
    """Check text from state['lastend'] to upto for literal context:

    - Within an enclosing '<pre>' preformatted region '</pre>'
    - Within an enclosing '<code>' code fragment '</code>'
    - Within a tag '<' body '>'

    We also update the state dict accordingly."""
    # XXX This breaks on badly nested angle brackets and <pre></pre>, etc.
    lastend, inpre, intag = state['lastend'], state['inpre'], state['intag']
    lastend = state['lastend']
    inpre, incode, intag = state['inpre'], state['incode'], state['intag']
    newintag = newincode = newinpre = 0
    text = lower(text)

    # Check whether '<pre>' is currently (possibly, still) prevailing.
    opening = rfind(text, '<pre>', lastend, upto)
    if (opening != -1) or inpre:
        if opening != -1: opening = opening + 4
        else: opening = lastend
        if -1 == rfind(text, '</pre>', opening, upto):
            newinpre = 1
    state['inpre'] = newinpre

    # Check whether '<code>' is currently (possibly, still) prevailing.
    opening = rfind(text, '<code>', lastend, upto)
    if (opening != -1) or incode:
        if opening != -1: opening = opening + 5
        # We must already be incode, start at beginning of this segment:
        else: opening = lastend
        if -1 == rfind(text, '</code>', opening, upto):
            newincode = 1
    state['incode'] = newincode

    # Determine whether we're (possibly, still) within a tag.
    opening = rfind(text, '<', lastend, upto)
    if (opening != -1) or intag:
        # May also be intag - either way, we skip past last <tag>:
        if opening != -1: opening = opening + 1
        # We must already be intag, start at beginning of this segment:
        else: opening = lastend
        if -1 == rfind(text, '>', opening, upto):
            newintag = 1
    state['intag'] = newintag

    state['lastend'] = after
    return newinpre or newincode or newintag

default__class_init__(CMFWikiPage)


class WikiNesting(Acquisition.Implicit):
    """Given a wiki dir, generate nesting relationship from parents info.

    In a nesting, nodes are represented as:
       - Leaves: the string name of the page
       - Nodes with children: a list beginning with the parent node's name
       - Nodes with omitted children (for brevity): list with one string.
    """
    # XXX We could make this a persistent object and minimize recomputes.
    #     Put it in a standard place in the wiki's folder, or have the
    #     wikis in a folder share an instance, but use a single
    #     persistent one which need not recompute all the relationship
    #     maps every time - just needs to compare all pages parents
    #     settings with the last noticed parents settings, and adjust
    #     the children, roots, and parents maps just for those that
    #     changed.  On this first cut we just recompute it all...

    def __init__(self, container, page_meta_type=CMFWikiPage.meta_type):
        self.container = container
        self.set_nesting(page_meta_type)

    def set_nesting(self, page_meta_type=None):
        """Preprocess for easy derivation of nesting structure.

        We set:
          - .parentmap: {'node1': ['parent1', ...], ...}
          - .childmap:  {'node1': ['child1', ...], ...}
          - .roots: {'root1': None, ...}"""

        allpageids, allpages = [], []
        for i, p in self.container.objectItems(spec=page_meta_type):
            allpageids.append(i)
            allpages.append(p)
        pagenames = []
        parentmap = {}                  # 'node': ['parent1', ...]
        childmap = {}                   # 'node': ['child1', ...]
        roots = {}
        for pg in allpages:
            parents = pg.parents
            if type(parents) != ListType: # SKWM
                parents = []
            pgnm = pg.getId()
            pagenames.append(pgnm)

            # We have a root if node has no parents (have to confirm their
            # existence):
            checkedparents = []
            for i in parents:
                if i in allpageids:
                    checkedparents.append(i)
            if not checkedparents:
                roots[pgnm] = None

            # Parents is direct:
            parentmap[pgnm] = checkedparents

            if not childmap.has_key(pgnm):
                childmap[pgnm] = []

            # Register page as child for all its (existing) parents:
            for p in checkedparents:
                # We can't just append, in case we're a persistent object
                # (which recognizes the need to update by an attr
                # assignment).
                if childmap.has_key(p): pchildren = childmap[p]
                else: pchildren = []
                if pgnm not in pchildren: pchildren.append(pgnm)
                childmap[p] = pchildren

        for k in parentmap.keys():
            parentmap[k].sort()
        for k in childmap.keys():
            childmap[k].sort()
        self.parentmap = parentmap
        self.childmap = childmap
        self.all = allpageids
        self.roots = roots

    def get_map(self):
        """Return nesting of entire wiki."""
        roots = self.roots.keys()
        roots.sort()
        did = {}
        got = self.get_offspring(roots, did=did)

        # Detect nodes involved in parenting loops and include them:
        leftovers = []
        for i in self.all:
            if not did.has_key(i):
                leftovers.append(i)
        if leftovers:
            leftovers.sort()
            got.extend(self.get_offspring(leftovers))

        return got
        
    def get_offspring(self, pages, did=None):
        """Return nesting showing all offspring of a list of wiki pagenames.

        did is used for recursion, to prune already elaborated pages.
        It can be used by the caller to detect pages that are in
        parenting loops, not reachable from any of the roots."""

        if did is None: did = {}
        got = []
        for p in pages:
            been_there = did.has_key(p)
            did[p] = None
            if self.childmap.has_key(p):
                children = self.childmap[p]
                if children:
                    subgot = [p]
                    if not been_there:
                        subgot.extend(self.get_offspring(children, did=did))
                    got.append(subgot)
                else:
                    got.append(p)
            else:
                got.append(p)
        return got

    def get_up_and_back(self, pagename):
        """Return nesting showing page containment and immediate offspring.
        """

        # Go up, identifying all and topmost forbears:
        ancestors = {}                  # Ancestors of pagename
        tops = {}                       # Ancestors that have no parents
        todo = {pagename: None}
        parentmap = self.parentmap
        while todo:
            doing = todo
            todo = {}
            for i in doing.keys():
                if ancestors.has_key(i):
                    continue            # We already took care of this one.
                else:
                    ancestors[i] = None
                    parents = None
                    if parentmap.has_key(i):
                        parents = parentmap[i]
                    if parents:
                        for p in parents:
                            todo[p] = None
                    else: tops[i] = None

        ancestors[pagename] = None      # Finesse page's offspring inclusion

        # Ok, now go back down, showing offspring of all intervening
        # ancestors: 
        tops = tops.keys()
        tops.sort
        did = {}; got = []
        childmap = self.childmap
        for t in tops:
            got.append(descend_ancestors(t, ancestors, did, childmap))
        return got

def _present_nesting_cur_node(rel, node, no_anchor=0):
    anchorexp = ((not no_anchor) and 'name="%s"' % quote(node)) or ''
    s = ('<font size="+2"><b><a %s href="%s/%s">%s</a></b></font>'
         % ((anchorexp, rel, quote(node), node)))
    return s
    
def present_nesting(myid, nesting, rel, no_anchors=0,
                    did=None, _got=None, indent=""):
    """Present an HTML outline of a nesting structure.

    _got is used internally and should not be passed in except when
    recursing.

    See WikiNesting docstring for nesting structure description."""
    if did is None: did = []
    if _got is None:
        _got = ["<ul>"]
        recursing = 0
    else:
        recursing = 1

    for n in nesting:

        if type(n) == ListType:
            anchorexp=((not no_anchors) and 'name="%s"' % quote(n[0])) or ''
            _got.append(indent + ' <li>')
            if n[0] == myid:
                # The is the current node - distinguish and show backlinks.
                # XXX Messy but expedient.
                _got.append(_present_nesting_cur_node(rel, n[0],
                                                      no_anchor=no_anchors))
            else:
                _got.append('<a %s href="%s/%s">%s</a>'
                            % (anchorexp, rel, quote(n[0]), n[0]))
            if len(n) > 1:
                _got.append("<ul>")
                for i in n[1:]:
                    if type(i) == ListType:
                        _got = present_nesting(myid, [i], rel, did=did,
                                               _got=_got, indent=indent+'  ',
                                               no_anchors=no_anchors)
                    else:
                        _got.append(indent + ' <li>')
                        if i == myid:
                            inm = "<strong>" + i + "</strong>"
                            # Distinguish that entry is for current node.
                            _got.append(_present_nesting_cur_node(
                                rel, i, no_anchor=no_anchors))
                        else:
                            anchorexp = (((not no_anchors)
                                          and 'name="%s"' % quote(i))
                                         or '')
                            inm = i
                            _got.append('<a %s href="%s/%s">%s</a>'
                                        % (anchorexp, rel, quote(i), i))
                _got.append("</ul>")
            elif recursing:
                # Parents whose children were omitted - indicate:
                _got[-1] = _got[-1] + " ..."
        else:
            if n == myid:
                # The entry is for the current node - distinguish.
                inm = "<strong>" + n + "</strong>"
            else: inm = n
            _got.append('%s <li><a name="%s" href="%s/%s">%s</a>'
                       % (indent, quote(n), rel, quote(n), inm))

    if recursing:
        return _got
    else:
        _got.append("</ul>")
        return join(_got, "\n")

def descend_ancestors(page, ancestors, did, children):
    """Create nesting of ancestors leading to page.

    page is the name of the subject page.
    ancestors is a mapping whose keys are pages that are ancestors of page
    children is a mapping whose keys are pages children, and the values
       are the children's parents.

    Do not repeat ones we already did."""
    got = []
    for c in ((children.has_key(page) and children[page]) or []):
        if not ancestors.has_key(c):
            # We don't descend offspring that are not ancestors.
            got.append(c)
        elif ((children.has_key(c) and children[c]) or []):
            if did.has_key(c):
                # We only show offspring of ancestors once...
                got.append([c])
            else:
                # ... and this is the first time.
                did[c] = None
                got.append(descend_ancestors(c, ancestors, did, children))
        else:
            got.append(c)
    got.sort()                  # Terminals will come before composites.
    got.insert(0, page)
    return got

def html_unquote(v, name='(Unknown name)', md={},
                 character_entities=(
                       (('&amp;'),    '&'),
                       (('&lt;'),    '<' ),
                       (('&gt;'),    '>' ),
                       (('&lt;'), '\213' ),
                       (('&gt;'), '\233' ),
                       (('&quot;'),    '"'))): #"
        text=str(v)
        for re,name in character_entities:
            if find(text, re) >= 0: text=join(split(text,re),name)
        return text

# Boldly taken from tres seaver's PTK code.
def parseHeadersBody( body, headers=None ):
    """Parse any leading 'RFC-822'-ish headers from an uploaded
    document, returning a tuple containing the headers in a dictionary
    and the stripped body.

    E.g.::

        Title: Some title
        Creator: Tres Seaver
        Format: text/plain
        X-Text-Format: structured

        Overview

        This document .....

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
    cr = re.compile( '^.*\r$' )
    lines = map( lambda x, cr=cr: cr.match( x ) and x[:-1] or x
               , split( body, '\n' ) )

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
            return headers, body     # no headers, just return those passed
        else:    # continuation
            last, hdrlist = hdrlist[ -1 ], hdrlist[ :-1 ]
            hdrlist.append( ( last[ 0 ]
                            , join( ( last[1], lstrip( line ) ), '\n' )
                            ) )
        i = i + 1

    for hdr in hdrlist:
        headers[ hdr[0] ] = hdr[ 1 ]

    return headers, join( lines[ i+1: ], '\n' )

def flatten(seq):
  """Translate a nested sequence into a flat list of string-terminals.
  We omit duplicates terminals in the process."""
  got = []
  pending = [seq]
  while pending:
    cur = pending.pop(0)
    if type(cur) == StringType:
      if cur not in got:
        got.append(cur)
    else:
      pending.extend(cur)
  return got

def initPageMetadata(page):
    page.creation_date = DateTime()
    page._editMetadata(title='',
                       subject=(),
                       description='',
                       contributors=(),
                       effective_date=None,
                       expiration_date=None,
                       format='text_html',
                       language='',
                       rights = '')


factory_type_information = (
    {'id': 'CMF Wiki Page',
     'content_icon': 'wikipage_icon.gif',
     'meta_type': 'CMF Wiki Page',
     'product': 'CMFWiki',
     'factory': 'addCMFWikiPage',
     'immediate_view': 'wikipage_view',
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'wikipage_view',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'comment',
                  'name': 'Comment',
                  'action': 'wikipage_comment_form',
                  'permissions': (CMFWikiPermissions.Comment,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'wikipage_edit_form',
                  'permissions': (CMFWikiPermissions.Edit,)},
                 {'id': 'history',
                  'name': 'History',
                  'action': 'wikipage_history',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'backlinks',
                  'name': 'Backlinks',
                  'action': 'wikipage_backlinks',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'advanced',
                  'name': 'Advanced',
                  'action': 'wikipage_advanced_form',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'toc',
                  'name': 'Wiki Contents',
                  'category': 'folder',
                  'action':'wikipage_toc',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'recent_changes',
                  'name': 'Recent Changes',
                  'category': 'folder',
                  'action':'wikipage_recentchanges',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'create',
                  'name': 'Create',
                  'category': 'folder',
                  'action':'wikipage_create_form',
                  'permissions': (CMFWikiPermissions.Create,),
                  'visible': 0 },
                 ),
     },
    {'id': 'CMF Wiki',
     'content_icon': 'folder_icon.gif',
     'meta_type': 'CMF Wiki',
     'description': ('Loosely organized (yet structured) content can be '
                     'added to Wikis.'),
     'product': 'CMFWiki',
     'factory': 'addCMFWikiFolder',
     'immediate_view': 'FrontPage',
     'actions': ({'id': 'toc',
                  'name': 'Wiki Contents',
                  'category': 'folder',
                  'action':'wiki_toc',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'view',
                  'name': 'FrontPage',
                  'category': 'folder',
                  'action':'FrontPage',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'all',
                  'name': 'All Pages',
                  'category': 'folder',
                  'action':'wiki_allpages',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'recent_changes',
                  'name': 'Recent Changes',
                  'category': 'folder',
                  'action':'wiki_recentchanges',
                  'permissions': (CMFWikiPermissions.View,)},
                 {'id': 'wikihelp',
                  'name': 'WikiHelp',
                  'category': 'folder',
                  'action': 'WikiHelp',
                  'permissions': (CMFWikiPermissions.View,)}
                 ),
     },
    )
     
default_perms = {
    'create': 'nonanon',
    'edit': 'nonanon',
    'comment': 'nonanon',
    'move': 'owners', # rename/delete/reparent
    'regulate': 'owners'
    }

class CMFWikiFolder( SkinnedFolder ):

    meta_type="CMF Wiki"

    def PUT_factory(self, name, typ, body):
        if find(typ, 'text') != -1:
            return makeCMFWikiPage(name, '', body)

    def Title(self): # for CMFCatalog
        fp = getattr( self, 'FrontPage', None )
        return fp and fp.Title() or self.title_or_id()

def makeCMFWikiPage(id, title, file):
    ob = CMFWikiPage(source_string=file, __name__=id)
    ob.title = title
    ob.parents = []
    username = getSecurityManager().getUser().getUserName()
    ob.manage_addLocalRoles(username, ['Owner'])
    ob.setSubOwner('both')
    initPageMetadata(ob)
    for name, perm in ob._perms.items():
        pseudoperm = default_perms[name]
        local_roles_map = ob._local_roles_map
        roles_map = ob._roles_map
        roles = (local_roles_map[name],) + roles_map[pseudoperm]
        ob.manage_permission(perm, roles=roles)
    return ob

def addCMFWikiPage(self, id, title='', file=''):
    id=str(id)
    title=str(title)
    ob = makeCMFWikiPage(id, title, file)
    self._setObject(id, ob)

def addCMFWikiFolder(self, id, title=''):
    id = str(id)
    title = str(title)
    ob = CMFWikiFolder(id, title)
    id = self._setObject(id, ob)
    ob = getattr(self, id)
    p = package_home(globals()) + os.sep + 'default_wiki_content'
    fnames = os.listdir(p)
    for fname in fnames:
        if fname[-5:] != '.wiki': continue
        f = open(p + os.sep + fname, 'r')
        fname = fname[:-5]
        addCMFWikiPage(ob, fname, title='', file=f.read())
        page = getattr(ob, fname)
        page.indexObject()
        # Hack - may be ok if we continue to have, like, only two pages:
        if fname == 'SandBox':
            page.parents = ['FrontPage']
