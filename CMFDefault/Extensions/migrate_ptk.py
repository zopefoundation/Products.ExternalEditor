from Acquisition import aq_base, aq_inner, aq_parent
from Globals import PersistentMapping
import sys


#
# Routines generally useful for migration purposes.
#


class Converter:
    def allowDescendChildren(self): raise 'Not implemented'
    def convert(self, ob): raise 'Not implemented'
    def showDuplicationError(self): raise 'Not implemented'


class Migrator:

    def __init__(self, conversions, skip):
        self.conversions = conversions
        self.skip = skip
        self.visited_folders = []
        self.warnings = []
        self.copied = []
        self.skipped = []

    def migrateObjectManager(self, src_folder, dst_folder, place=()):
        self.visited_folders.append( '/'.join(place) )
        for id, s_ob in src_folder.objectItems():
            d_ob = getattr(dst_folder, id, None)
            to_store = self.migrateObject(id, s_ob, d_ob, dst_folder,
                                          place + (id,))
            if to_store is not None:
                owner = getattr(to_store, '_owner', None)
                if hasattr(dst_folder, '_setObject'):
                    dst_folder._setObject(id, to_store)
                else:
                    setattr(dst_folder, id, to_store)
                if owner is not None:
                    # Retain ownership.
                    to_store._owner = owner

    def migrateDiscussionContainer(self, src_folder, dst_folder, place=()):
        self.visited_folders.append( '/'.join(place) )
        dst_container = getattr(dst_folder, '_container', None)
        if dst_container is None:
            dst_container = dst_folder._container = PersistentMapping()
        for id, s_ob in src_folder._container.items():
            d_ob = dst_container.get(id)
            to_store = self.migrateObject(id, s_ob, d_ob, dst_folder,
                                          place + (id,))
            if to_store is not None:
                dst_container[id] = aq_base(to_store)

    def migratePossibleContainer(self, s_ob, d_ob, place):
        base_ob = aq_base(s_ob)
        if hasattr(base_ob, 'objectItems'):
            self.migrateObjectManager(s_ob, d_ob, place)
        elif hasattr(base_ob, '_container'):
            self.migrateDiscussionContainer(s_ob, d_ob, place)

    def migrateObject(self, id, s_ob, d_ob, dst_folder, place):
        # Doesn't store changes, only returns the
        # object to store.
        conversions = self.conversions
        klass = s_ob.__class__
        descend_ok = 1
        base_ob = aq_base(s_ob)
        to_store = None
        pathname = '/'.join(place)
        if self.skip.has_key(id):
            # Don't migrate objects by this name, but we can still
            # migrate subobjects.
            descend_ok = self.skip[id]
            if descend_ok and d_ob is None:
                descend_ok = 0
            self.skipped.append(pathname +
                               (descend_ok and ' (descended)' or ' '))
        elif d_ob is not None:
            # The dest already has something with this ID.
            descend_ok = 1
            show_message = 1
            converter = conversions.get(klass, None)
            if converter is not None:
                descend_ok = converter.allowDescendChildren()
                show_message = converter.showDuplicationError()
            if show_message:
                self.warnings.append('Already existed: %s' % pathname)
        elif conversions.has_key(klass):
            # Invoke the appropriate converter.
            converter = conversions[klass]
            to_store = converter.convert(s_ob)
            self.copied.append(pathname)
        elif hasattr(base_ob, '_getCopy'):
            # Make a direct copy.
            to_store = s_ob._getCopy(dst_folder)
            self.warnings.append('Copied %s directly.' % pathname)
            descend_ok = 0
        else:
            # No way to copy.
            descend_ok = 0
            self.warnings.append('Could not copy %s' % pathname)
        if descend_ok:
            if to_store is not None:
                d_ob = to_store
            if d_ob is not None:
                try: d_ob._p_jar = dst_folder._p_jar
                except: pass
                self.migratePossibleContainer(s_ob, d_ob, place)
        return to_store


class SimpleClassConverter (Converter):
    def __init__(self, to_class, descend, show_dup=1):
        self._klass = to_class
        self._descend = descend
        self._show_dup = show_dup

    def allowDescendChildren(self):
        return self._descend

    def showDuplicationError(self):
        return self._show_dup

    def convert(self, ob):
        # Creates a copy of ob without its children.
        ob = aq_base(ob)
        k = self._klass
        if hasattr(k, '__basicnew__'):
            newob = k.__basicnew__()
        else:
            newob = new.instance(k, {})
        id = ob.id
        if callable(id):
            id = id()
        try: newob._setId(id)
        except AttributeError: newob.id = id
        newob.__dict__.update(ob.__dict__)
        if hasattr(newob, '_objects'):
            # Clear the children.
            for info in newob._objects:
                del newob.__dict__[info['id']]
            newob._objects = ()
        if hasattr(newob, '_container'):
            # Clear the children.
            newob._container = PersistentMapping()
        return newob

TupleType = type(())

def setupDirectConversion(old_prod, new_prod, modname, classname,
                          conversions, descend=1, show_dup=1):
    try:
        old_module = sys.modules['Products.' + old_prod + '.' + modname]
        new_module = sys.modules['Products.' + new_prod + '.' + modname]
        old_class = getattr(old_module, classname)
        new_class = getattr(new_module, classname)
        conversions[old_class] = SimpleClassConverter(new_class, descend,
                                                      show_dup)
    except:
        print 'Failed to set up conversion', old_prod, new_prod, modname, classname
        import traceback
        traceback.print_exc()


def setupDirectConversions(old_prod, new_prod, modnames, conversions):
    for info in modnames:
        if type(info) is TupleType:
            modname, classname = info
        else:
            modname = classname = info
        setupDirectConversion(old_prod, new_prod, modname, classname,
                              conversions)


def _cleanupOwnership(ob, res, cleanup_children):
    '''
    If the user name of the owner of the referenced object
    is not found in its current user database but is found
    in the local user database, this function changes the
    ownership of the object to the local database.
    '''
    try: changed = ob._p_changed
    except: changed = 0

    owner = getattr(ob, '_owner', None)
    if owner:
        udb, uid = owner
        #res.append('Owner of %s is %s!%s' % (
        #    '/'.join( ob.getPhysicalPath() ), '/'.join(udb), uid,))
        root = ob.getPhysicalRoot()
        try:
            db = root.unrestrictedTraverse(udb, None)
            user = db.getUserById(uid)
            if hasattr(ob, 'aq_inContextOf'):
                ucontext = aq_parent(aq_inner(db))
                if not ob.aq_inContextOf(ucontext):
                    # Not in the right context.
                    user = None
        except:
            user = None
        if user is None:
            # Try to change to a local database.
            p = ob
            old_udb = udb
            udb = None
            while p is not None:
                if hasattr(p, 'acl_users'):
                    acl_users = p.acl_users
                    try:
                        user = acl_users.getUserById(uid)
                    except:
                        user = None
                    if user is not None:
                        # Found the right database.
                        udb = acl_users.getPhysicalPath()[1:]
                        break
                p = aq_parent(aq_inner(p))
            if udb is not None:
                ob._owner = udb, uid
                res.append('Changed ownership of %s from %s!%s to %s!%s' %
                           ('/'.join( ob.getPhysicalPath() ),
                            '/'.join(old_udb), uid,
                            '/'.join(udb), uid,))
            else:
                res.append('Could not fix the ownership of %s, '
                           'which is set to %s!%s' %
                           ('/'.join( ob.getPhysicalPath() ),
                            '/'.join(old_udb), uid,))

    if cleanup_children:
        if hasattr(ob, 'objectValues'):
            for subob in ob.objectValues():
                _cleanupOwnership(subob, res, 1)

    # Deactivate object if possible.
    if changed is None: ob._p_deactivate()

    return res

def _copyUsers(src_folder, dst_folder):
    source = src_folder.acl_users
    target = dst_folder.acl_users
    for user in source.getUsers():
        target._addUser(name=user.name, password=user.__, confirm=user.__,
                        roles=user.roles, domains=user.domains, REQUEST=None)

#
# PTK to CMF Migration script.
#


def migrate(self, src_path='', dest_path='', copy_users=0, ownership_only=0):
    if not src_path or not dest_path:
        return '''
        <html><body><form action="%s" method="POST">
        <h2>Migrate PTK content to CMF site</h2>
        <p>Path (not including server URL) to PTK instance (source):
        <input type="text" name="src_path"></p>
        <p>Path (not including server URL) to CMF site (destination):
        <input type="text" name="dest_path"></p>
        <p>Copy users:
        <input type="checkbox" name="copy_users" value="1"></p>
        <input type="submit" name="submit" value="Migrate">
        <input type="submit" name="ownership_only"
        value="Just clean up ownership">
        </form></body></html>
        ''' % self.REQUEST['URL']
    root = self.getPhysicalRoot()
    dst_folder = root.restrictedTraverse(dest_path)
    if not ownership_only:
        src_folder = root.restrictedTraverse(src_path)
        if copy_users:
            _copyUsers(src_folder, dst_folder)
        m = Migrator(ptk2cmf_conversions, ptk2cmf_skip)
        m.migrateObjectManager(src_folder, dst_folder)
    ownership_res = []
    _cleanupOwnership(dst_folder, ownership_res, 1)
    return '''
        <html><body><p>Finished migration.</p>
        <p>Warnings (if any):<ul><li>%s</li></ul></p>
        <p>Visited folders:<ul><li>%s</li></ul></p>
        <p>Skipped:<ul><li>%s</li></ul></p>
        <p>Converted content:</p><pre>%s</pre>
        <p>Fixed up ownership:</p><pre>%s</pre>
        </body></html>
        ''' % ('</li>\n<li>'.join(m.warnings),
               '</li>\n<li>'.join(m.visited_folders),
               '</li>\n<li>'.join(m.skipped),
               '\n'.join(m.copied),
               '\n'.join(ownership_res),
               )

migrate_ptk = migrate

#
# PTK to CMF Conversion definitions.
#


ptk2cmf_conversions = {}

ptk2cmf_skip = {
    'portal_actions':0,
    'portal_catalog':0,
    'portal_discussion':0,
    'portal_memberdata':0,
    'portal_membership':0,
    'portal_properties':0,
    'portal_registration':0,
    'portal_skins':1,
    'portal_types':0,
    'portal_undo':0,
    'portal_url':0,
    'portal_workflow':0,
    'MailHost':0,
    'cookie_authentication':0,
    }

demo_conversions = (
    'Document',
    'NewsItem',
    'Image',
    'File',
    'Link',
    'Favorite',
    'DiscussionItem',
    ('DiscussionItem', 'DiscussionItemContainer'),
    )


BEFORE_CONTENT_MOVE = 0

if BEFORE_CONTENT_MOVE:
    content_product = 'PTKBase'
else:
    content_product = 'PTKDemo'


setupDirectConversions(content_product, 'CMFDefault', demo_conversions,
                       ptk2cmf_conversions)

setupDirectConversion('PTKBase', 'CMFCore', 'DirectoryView', 'DirectoryView',
                       ptk2cmf_conversions, 0, 0)

setupDirectConversion('PTKBase', 'CMFCore', 'PortalFolder', 'PortalFolder',
                       ptk2cmf_conversions, 1)

from OFS.Folder import Folder
from Products.CMFCore.PortalFolder import PortalFolder
ptk2cmf_conversions[Folder] = SimpleClassConverter(PortalFolder, 1)
