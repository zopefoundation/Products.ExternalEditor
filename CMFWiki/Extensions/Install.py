"""
This file is an installation script for CMFWiki.  It's meant to be
used as an External Method.  To use, add an external method to the
root of the CMF Site that you want CMF Wiki registered in with the
configuration:

 id: install_cmfwiki
 title: Install CMFWiki *optional*
 module name: CMFWiki.Install
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  The install function will execute and give
information about the steps it took to register and install the CMF Wiki
into the CMF Site instance.
"""
__version__='$Revision$'[11:-2]

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFWiki import CMFWikiPage, wiki_globals
from ZODB.PersistentMapping import PersistentMapping
from cStringIO import StringIO
import string

def install(self):
    " Register the CMF Topic with portal_types and friends "
    out = StringIO()
    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')
    workflowtool = getToolByName(self, 'portal_workflow')
    
    # Borrowed from CMFDefault.Portal.PortalGenerator.setupTypes()
    # We loop through anything defined in the factory type information
    # and configure it in the types tool if it doesn't already exist
    for t in CMFWikiPage.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(t['id'], cfm)
            out.write('Registered %s with the types tool\n' % t['id'])
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                t['id']))

     # Setup the skins
     # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    if 'wiki' not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', wiki_globals)
        out.write("Added 'wiki' directory view to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # 'wiki' into the configurations.  Preferably, this should be
    # right before where 'content' is placed.  Otherwise, we append
    # it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        for dir in ( 'wiki', 'zpt_wiki' ):

            if not dir in path:
                try:
                    idx = path.index( 'custom' )
                except ValueError:
                    idx = 999
                path.insert( idx+1, dir )

        path = string.join(path, ', ')
        # addSkinSelection will replace existing skins as well.
        skinstool.addSkinSelection(skin, path)
        out.write("Added 'wiki' and 'zpt_wiki' to %s skin\n" % skin)

    # remove workflow for Wiki pages
    cbt = workflowtool._chains_by_type
    if cbt is None:
        cbt = PersistentMapping()
    cbt['CMF Wiki'] = []
    cbt['CMF Wiki Page'] = []
    workflowtool._chains_by_type = cbt
    out.write("Removed all workflow from CMF Wikis and CMF Wiki Pages")
    return out.getvalue()
