""" CMFWiki product permissions

$Id$
"""
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFWiki.permissions')

security.declarePublic('View')
from Products.CMFCore.permissions import View

security.declarePublic('Move')
Move = 'Move CMFWiki Page'

security.declarePublic('Edit')
Edit = 'Edit CMFWiki Page'

security.declarePublic('Comment')
Comment = 'Add CMFWiki Comment'

security.declarePublic('Create')
Create = 'Create CMFWiki Page'

security.declarePublic('Regulate')
Regulate = 'Change CMFWiki Regulations'

security.declarePublic('FTPRead')
FTPRead = 'FTP access'
