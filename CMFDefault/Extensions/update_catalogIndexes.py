from Products.CMFCore.utils import getToolByName

def update_catalogIndexes(self, REQUEST):
    '''
    External method to drop, re-add, and rebuild catalog Indexes for migrated 
    CMF sites from Zope 2.3 to 2.4+.
    '''
    rIndexes = {'allowedRolesAndUsers': 'KeywordIndex'
              , 'effective': 'FieldIndex'
              , 'expires': 'FieldIndex'}
    ct = getToolByName(self, 'portal_catalog')
    map(lambda x, ct=ct: ct.delIndex(x), rIndexes.keys())
    map(lambda x, ct=ct: ct.addIndex(x[0], x[1]), rIndexes.items()) 
    ct.manage_reindexIndex(ids=rIndexes.keys(), REQUEST=REQUEST)
    return 'Catalog Indexes rebuilt.'
