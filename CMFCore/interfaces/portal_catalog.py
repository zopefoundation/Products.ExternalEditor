##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

"""Catalog tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]


from Interface import Attribute, Base

class portal_catalog(Base):
    '''This tool interacts with a customized ZCatalog.
    '''
    id = Attribute('id', 'Must be set to "portal_catalog"')

    # searchResults inherits security assertions from ZCatalog.
    def searchResults(REQUEST=None, **kw):
        '''Calls SiteIndex.searchResults() with extra arguments that
        limit the results to what the user is allowed to see.
        '''

    # __call__ inherits security assertions from ZCatalog.
    def __call__(REQUEST=None, **kw):
        '''Same as searchResults().'''

    # indexObject__roles__ = ()  # Called only by Python code.
    def indexObject(object):
        '''Add to catalog.
        '''

    # unindexObject__roles__ = ()
    def unindexObject(object):
        '''Remove from catalog.
        '''

    # reindexObject__roles__ = ()
    def reindexObject(object):
        '''Update entry in catalog.
        '''

    # getpath inherits security assertions from ZCatalog.
    def getpath(data_record_id_):
        '''Calls ZCatalog.getpath().
        '''
