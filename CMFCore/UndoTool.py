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
from AccessControl import ClassSecurityInfo, Unauthorized
from Expression import Expression
from ActionInformation import ActionInformation
from ActionProviderBase import ActionProviderBase
from CMFCorePermissions import ManagePortal, UndoChanges, ListUndoableChanges

class UndoTool (UniqueObject, SimpleItem, ActionProviderBase):
    id = 'portal_undo'
    meta_type = 'CMF Undo Tool'
    # This tool is used to undo changes.
    _actions = [ActionInformation(id='undo'
                                , title='Undo'
                                , action=Expression(
               text='string: ${portal_url}/undo_form')
                                , condition=Expression(
               text='member') 
                                , permissions=(ListUndoableChanges,)
                                , category='global'
                                , visible=1
                                 )]


    security = ClassSecurityInfo()

    manage_options = ( ActionProviderBase.manage_options +
                       SimpleItem.manage_options +
                       ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ))
    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainUndoTool', _dtmldir )

    security.declarePrivate('listActions')
    def listActions(self, info=None):
        """
        List actions available through tool
        """
        return self._actions

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

    security.declarePublic('undo')
    def undo(self, object, transaction_info):
        """
            Undo the list of transactions passed in 'transaction_info',
            first verifying that the current user is allowed to undo them.
        """
        # Belt and suspenders:  make sure that the user is actually
        # allowed to undo the transation(s) in transaction_info.

        xids = {}  # set of allowed transaction IDs

        allowed = self.listUndoableTransactionsFor( object )

        for xid in map( lambda x: x['id'], allowed ):
            xids[xid] = 1

        if type( transaction_info ) == type( '' ):
            transaction_info = [ transaction_info ]

        for tinfo in transaction_info:
            if not xids.get( tinfo, None ):
                raise Unauthorized

        object.manage_undo_transactions(transaction_info)


InitializeClass(UndoTool)
