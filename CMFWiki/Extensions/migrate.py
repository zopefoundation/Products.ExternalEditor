"""Utilities to transfer the contents of an old WikiForNow wiki to CMFWiki."""

import os, string, sys
import Zope
from Products.CMFWiki.CMFWikiPage \
     import CMFWikiPage, addCMFWikiFolder, addCMFWikiPage

from Acquisition import aq_base, aq_parent, aq_inner
from OFS import SimpleItem
from Products.ZWiki import ZWikiPage
from ZPublisher.Request import Request
from ZPublisher.Response import Response
from types import StringType

old_folder_suffix = '_old_ZWiki'
new_folder_suffix = '_new_CMFWiki'

DIRNM = os.path.split(__file__)[0]

app = Zope.app()

IGNORE_PGS = ['HelpPage',
              'HowDoIEdit',
              'HowDoINavigate',
              'RegulatingYourPages',
              'StructuredText',
              'StructuredTextExample',
              'StructuredTextRules',
              'TextFormattingRules',
              'WikiName',
              'WikiWikiWeb',
              'ZWiki',
              'ZWikiLinks',
              'ZWikiWeb', 
              'editform',
              'commentform',
              'standard_wiki_header',
              'standard_wiki_footer',
              'advancedform',
              'pagehistory',
              'backlinks',
              'JumpTo',
              'AllPages',
              'RecentChanges',
              'SearchPage',
              'backlinksBF',
              'backlinksZC',
              'minimal_footer',
              'AllPagesBF',
              'AllPagesZC',
              'editform_multiformat',
              'editform_simple',
              'JumpToBF',
              'JumpToZC',
              'RecentChangesBF',
              'RecentChangesZC',
              'SearchPageBF',
              'SearchPageZC',
              ]

# =================
# Top level driver
# =================

def do_site(folder=app, REQUEST=None):
    """Create copies of existing 'ZWiki Page' folders as CMFWiki folders.

    This function hunts down all folders that have a FrontPage item with
    meta_type 'ZWiki Page'.  It results in the old folder being moved aside,
    to the original name with "_old_ZWiki" appended, and the new folder with
    all pages (except obsolete ZWiki standard pages) in its place.

    We actually create copies of the relevant pages in a new folder, move the
    old one aside (to name_old_ZWiki), then move the new folder in place.

    If, for folder 'name', we find an existing 'name_old_ZWiki', we skip this
    folder.

    If we find an existing 'name_new_CMFWiki', we presume it is residue from
    an interrupted prior run and overwrite it with the new stuff, then moving
    it in place of the original ZWiki folder."""

    # Get the total number of pages on the site, and incidentally prime the
    # cache:
    print ("Searching for undone ZWiki Page folders..."
           % string.join(folder.getPhysicalPath(), '/'))
    undone, done = cull_done(locate(name='FrontPage', type='ZWiki Page',
                                    folder=folder))
    print "%s ZWiki Page folders to do (%s already done)" % (len(undone),
                                                             len(done))

    if not undone:
        print 'Nothing to do...'
        return None

    foldercount = pagecount = skipcount = noncount = failedcount = 0
    for subject in undone:

        container = aq_parent(aq_inner(subject))

        got = duplicate_as_CMFWiki(subject, new_folder_suffix)
        foldercount = foldercount + 1
        new, pages, non, skips, failed = got
        pagecount = pagecount + pages
        failedcount = failedcount + failed
        skipcount = skipcount + skips
        noncount = noncount + non

        mainid = subject.id
        asideid = mainid + old_folder_suffix

        container._delObject(mainid)
        subject.id = asideid
        container._setObject(asideid, aq_base(subject))

        container._delObject(new.id)
        new.id = mainid
        container._setObject(mainid, new)
        if not (foldercount % 100):
            print "%d folders done..." % foldercount

    msg = ("Did %d folders:"
           " %d wiki pages, %d non-wiki, %s obsolete, %s failed."
           % (len(undone), pagecount, noncount, skipcount, failedcount))
    print msg
    print "Old folders left suffixed with '%s'" % old_folder_suffix
    return msg

def duplicate_as_CMFWiki(subject, new_suffix):
    """Copy ZWiki folder subject into a fresh new CMFWiki folder.

    The new folder will get the old name + new_suffix.

     - Don't copy members of ignore_pgs, what else?
     - For other types of pages, include them in the new place as ref!
     - Uncatalog *all* old pages, ignored or not.
     - (XXX Make sure CMF wiki maker sets ownership properly.)"""

    container = aq_parent(subject)
    newid = subject.id + new_suffix
    addCMFWikiFolder(container, newid, subject.title)
    new = container[newid]
    pages = non = skips = failed = 0
    for i in subject.objectIds():
        if i in IGNORE_PGS:
            skips = skips + 1
            continue
        oldpage = getattr(subject, i)
        if oldpage.meta_type == 'ZWiki Page':
            duplicate_CMFWikiPage(oldpage, new)
            pages = pages + 1
        else:
            # Put a reference to the old object in the new place.
            # XXX!  Will this preserve the object across ZMI 'delete' of the
            #       old folder?
            id = oldpage.id
            if type(id) != StringType: id = id()
            try:
                new._setObject(id, oldpage)
                non = non + 1
            except:
                failed = failed + 1
                print ("Skipping %s: %s '%s'"
                       % (string.join(oldpage.getPhysicalPath(), '.'),
                          sys.exc_info()[0],
                          sys.exc_info()[1]))

    return new, pages, non, skips, failed

STDPROPS = map(lambda x: x['id'], ZWikiPage.ZWikiPage._properties)

def duplicate_CMFWikiPage(oldpage, newfolder):
    """Copy ZWiki page as CMFWiki page in new CMFWiki folder.

     - Transfer all properties - parents, etc.
     - Retain 'Owner' local role and ownership.
     - Recatalog page.
     - Translate regulation settings."""
    id = oldpage.id()
    if hasattr(aq_base(newfolder), id):
        newpage = getattr(newfolder, id)
        newpage.title = oldpage.title
        newpage.raw = oldpage.raw
    else:
        addCMFWikiPage(newfolder, id, title=oldpage.title, file=oldpage.raw)
        newpage = getattr(newfolder, id)

    # 'Responsibility' ownership:
    if hasattr(oldpage, '_owner'):
        newpage._owner = oldpage._owner

    # Local roles:
    for k, v in newpage.get_local_roles():
        newpage.manage_delLocalRoles([k])
    for k, v in oldpage.get_local_roles():
        newpage.manage_setLocalRoles(k, v)

    # Regulation permissions:
    for op in oldpage.regOps():
        newpage.setOp(op, oldpage.opUsernames(op), oldpage.opCategory(op))

    # Properties:
    for prop in STDPROPS:
        setattr(newpage, prop, getattr(oldpage, prop))

    # Catalog:
    newpage.reindexObject()

def cull_done(frontpages):
    """Return a tuple of undone folders and already done folders."""
    undone = []
    done = []
    for i in frontpages:
        folder = i._my_folder()
        id = i.id
        if type(id) != StringType:
            id = id()
        if old_folder_suffix == id[-len(old_folder_suffix):]:
            done.append(folder)
        else:
            undone.append(folder)
    return undone, done

def locate(name=None, type=None, folder=app):
    """Descend into folder hierarchy returning objects according to criteria.

    name: restrict attention to objects with id == name

    type: restrict attention to objects with meta_type == type

    Search starts in specified folder, defaulting to the application root.
    """
    got = []
    fb = aq_base(folder)                # To avoid acquiring in lookups.
    if name is None:
        got.extend(fb.objectValues())
    elif hasattr(fb, name):
        it = getattr(fb, name)
        if not type or it.meta_type == type:
            got.append(aq_base(it).__of__(folder))
    for subf in folder.objectValues(spec=['Folder', 'Product',
                                          'Portal Folder', 'CMF Site']):
        got.extend(locate(name=name, type=type,
                          # Ensure that subf acquires properly from folder.
                          folder=aq_base(subf).__of__(folder)))
    return got
