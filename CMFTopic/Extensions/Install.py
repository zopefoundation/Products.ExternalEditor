from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFTopic import Topic, topic_globals
from cStringIO import StringIO
import string

def install(self):
    " Register the CMF Topic with portal_types and friends "
    out = StringIO()
    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')

    # Borrowed from CMFDefault.Portal.PortalGenerator.setupTypes()
    for t in Topic.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(t['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                t['id']))

    # Setup the skins
    # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    if 'topic' not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', topic_globals)
        out.write("Added 'topic' directory view to portal_skins\n")
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'topic' not in path:
            try: path.insert(path.index('content'), 'topic')
            except ValueError:
                path.append('topic')
                
            path = string.join(path, ', ')
            # addSkinSelection will replace exissting skins as well.
            skinstool.addSkinSelection(skin, path)
            out.write("Added 'topic' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'topic' is already set up\n" % (
                skin))

    return out.getvalue()

