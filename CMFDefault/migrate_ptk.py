

from Acquisition import aq_base, aq_inner, aq_parent
from string import join
import sys


#
# Routines generally useful for migration purposes.
#


class MigrationResults:
    def __init__(self):
        self.visited_folders = []
        self.warnings = []
        self.copied = []
        self.skipped = []


class Converter:
    def allowDescendChildren(self): raise 'Not implemented'
    def convert(self, ob): raise 'Not implemented'
    def showDuplicationError(self): raise 'Not implemented'


def pathOf(ob):
    return join(ob.getPhysicalPath(), '/')

def _migrateObjectManager(src_folder, dst_folder, conversions, skip, res):
    res.visited_folders.append(pathOf(src_folder))
    for id, s_ob in src_folder.objectItems():
        _migrateObject(id, s_ob, dst_folder, conversions, skip, res)

def _migrateContainer(src_folder, dst_folder, conversions, skip, res):
    res.visited_folders.append(pathOf(src_folder))
    for id, ob in src_folder._container.items():
        s_ob = ob.__of__(src_folder)
        _migrateObject(id, s_ob, dst_folder, conversions, skip, res)

def _migrateObject(id, s_ob, dst_folder, conversions, skip, res):
    klass = s_ob.__class__
    descend_ok = 1
    pathname = pathOf(s_ob)
    base_ob = aq_base(s_ob)
    if skip.has_key(id):
        descend_ok = skip[id]
        if descend_ok and not hasattr(aq_base(dst_folder), id):
            descend_ok = 0
        res.skipped.append(pathname +
                           (descend_ok and ' (descended)' or ' '))
    elif hasattr(aq_base(dst_folder), id):
        descend_ok = 1
        show_message = 1
        converter = conversions.get(klass, None)
        if converter is not None:
            descend_ok = converter.allowDescendChildren()
            show_message = converter.showDuplicationError()
        if show_message:
            res.warnings.append('Folder %s already had an '
                                'attribute named %s.'
                                % (pathOf(dst_folder), id))
    elif conversions.has_key(klass):
        converter = conversions[klass]
        d_ob = converter.convert(s_ob)
        dst_folder._setObject(id, d_ob)
        if hasattr(base_ob, '_owner'):
            # Retain ownership.
            d_ob._owner = s_ob._owner
        res.copied.append(pathname)
    elif hasattr(base_ob, '_getCopy'):
        d_ob = s_ob._getCopy(dst_folder)
        dst_folder._setObject(id, d_ob)
        if hasattr(base_ob, '_owner'):
            # Retain ownership.
            d_ob._owner = s_ob._owner
        res.warnings.append('Copied %s directly.' % pathname)
        descend_ok = 0
    else:
        descend_ok = 0
        res.warnings.append('Could not copy %s' % pathname)
    if descend_ok:
        if hasattr(base_ob, 'objectItems'):
            _migrateObjectManager(s_ob, dst_folder._getOb(id),
                                  conversions, skip, res)
        elif hasattr(base_ob, '_container'):
            _migrateContainer(s_ob, dst_folder._getOb(id),
                              conversions, skip, res)


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
        ob = aq_base(ob)
        k = self._klass
        if hasattr(k, '__basicnew__'):
            newob = k.__basicnew__()
        else:
            newob = new.instance(k, {})
        try: newob.id = ob.id
        except AttributeError: pass
        newob.__dict__.update(ob.__dict__)
        if hasattr(newob, '_objects'):
            # Clear the children.
            for info in newob._objects:
                del newob.__dict__[info['id']]
            newob._objects = ()
        if hasattr(newob, '_container'):
            # Clear the children.
            newob._container.clear()
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
        #    join(ob.getPhysicalPath(), '/'), join(udb, '/'), uid,))
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
                           (join(ob.getPhysicalPath(), '/'),
                            join(old_udb, '/'), uid,
                            join(udb, '/'), uid,))
            else:
                res.append('Could not fix the ownership of %s, '
                           'which is set to %s!%s' %
                           (join(ob.getPhysicalPath(), '/'),
                            join(old_udb, '/'), uid,))
                
    if cleanup_children:
        if hasattr(ob, 'objectValues'):
            for subob in ob.objectValues():
                _cleanupOwnership(subob, res, 1)

    # Deactivate object if possible.
    if changed is None: ob._p_deactivate()
    
    return res


#
# PTK to CMF Migration script.
#


def migrate(self, src_path='', dest_path=''):
    if not src_path or not dest_path:
        return '''
        <html><body><form action="%s" method="POST">
        <p>Migrate PTK content to CMF site</p>
        <p>Path (not including "http://") to PTK instance (source):
        <input type="text" name="src_path"></p>
        <p>Path (not including "http://") to CMF site (destination):
        <input type="text" name="dest_path"></p>
        <input type="submit" name="submit" value="Migrate">
        </form></body></html>
        ''' % self.REQUEST['URL']
    root = self.getPhysicalRoot()
    src_folder = root.restrictedTraverse(src_path)
    dst_folder = root.restrictedTraverse(dest_path)
    res = MigrationResults()
    _migrateObjectManager(src_folder, dst_folder,
                          ptk2cmf_conversions, ptk2cmf_skip, res)
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
        ''' % (join(res.warnings, '</li>\n<li>'),
               join(res.visited_folders, '</li>\n<li>'),
               join(res.skipped, '</li>\n<li>'),
               join(res.copied, '\n'),
               join(ownership_res, '\n'),
               )


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

setupDirectConversions('PTKDemo', 'CMFDefault', demo_conversions,
                       ptk2cmf_conversions)

setupDirectConversion('PTKBase', 'CMFCore', 'DirectoryView', 'DirectoryView',
                       ptk2cmf_conversions, 0, 0)

setupDirectConversion('PTKBase', 'CMFCore', 'PortalFolder', 'PortalFolder',
                       ptk2cmf_conversions, 1)

from OFS.Folder import Folder
from Products.CMFCore.PortalFolder import PortalFolder
ptk2cmf_conversions[Folder] = SimpleClassConverter(PortalFolder, 1)
