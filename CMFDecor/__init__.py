
from Products.CMFCore import DirectoryView, utils
import FSPageTemplate

utils.registerIcon(FSPageTemplate.FSPageTemplate,
                   'images/fspt.gif', globals())

DirectoryView.registerDirectory('skins', globals())

def initialize(context):
    pass
