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

"""Basic undo tool.
$Id$
"""
__version__='$Revision$'[11:-2]


from utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from string import split
from AccessControl import ClassSecurityInfo

from CMFCorePermissions import ManagePortal, UndoChanges, ListUndoableChanges

class UndoTool (UniqueObject, SimpleItem):
    id = 'portal_undo'
    meta_type = 'CMF Undo Tool'
    # This tool is used to undo changes.


    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainUndoTool', _dtmldir )

    security.declarePrivate('listActions')
    def listActions( self, info ):
        if info.isAnonymous:
            return []
        return [ { 'name': 'Undo'
                 , 'url': 'undo_form'
                 , 'permissions': [ ListUndoableChanges ]
                 , 'category': 'global'
                 } ]

    #
    #   'portal_undo' interface methods
    #
    security.declareProtected( ListUndoableChanges
                             , 'listUndoableTransactionsFor')
    def listUndoableTransactionsFor(self, object,
                                    first_transaction=None,
                                    last_transaction=None,
                                    PrincipiaUndoBatchSize=None):
        '''Lists all transaction IDs the user is allowed to undo.
        '''
        # arg list for undoable_transactions() changed in Zope 2.2.
        portal = self.aq_inner.aq_parent
        transactions = portal.undoable_transactions(
            first_transaction=first_transaction,
            last_transaction=last_transaction,
            PrincipiaUndoBatchSize=PrincipiaUndoBatchSize)
        if not _checkPermission('Manage portal', portal):
            # Filter out transactions done by other members of the portal.
            user_name = _getAuthenticatedUser(self).getUserName()
            transactions = filter(
                lambda record, user_name=user_name:
                split(record['user_name'])[-1] == user_name,
                transactions
                )
        return transactions
        

    security.declareProtected(UndoChanges, 'undo')
    def undo(self, object, transaction_info):
        '''Performs an undo operation.
        '''
        object.manage_undo_transactions(transaction_info)


InitializeClass(UndoTool)
