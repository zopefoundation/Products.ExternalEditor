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
""" Undo tool interface.

$Id$
"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class portal_undo(Interface):
    '''Provides access to Zope undo functions.
    '''
    id = Attribute('id', 'Must be set to "portal_undo"')

    # permission: 'Undo changes'
    def listUndoableTransactionsFor(object,
                                    first_transaction=None,
                                    last_transaction=None,
                                    PrincipiaUndoBatchSize=None):
        '''Lists all transaction IDs the user is allowed to undo.
        '''

    # permission: 'Undo changes'
    def undo(object, transaction_info):
        '''Performs an undo operation.
        '''
