import CMFWikiPage
from CMFWikiPermissions import Create

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.PortalFolder import PortalFolder

registerDirectory('skins', globals())

def initialize(context):
    # CMF Initializers
    utils.ContentInit(
        'CMF Wiki Content',
        content_types = (CMFWikiPage.CMFWikiPage, PortalFolder),
        permission = Create,
        extra_constructors = (CMFWikiPage.addCMFWikiPage,
                              CMFWikiPage.addCMFWikiFolder),
        fti = CMFWikiPage.factory_type_information,
        ).initialize(context)
        
