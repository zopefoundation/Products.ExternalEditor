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

"""Skins tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]

from Interface import Attribute, Base

class portal_skins(Base):
    '''An object that provides skins to a portal object.
    '''
    id = Attribute('id', 'Must be set to "portal_skins"')

    # getSkin__roles__ = ()  # Private
    def getSkin(request):
        '''
        Returns the requested skin object as a tuple:
        (skinob, skinpath).  Note that self will not normally
        be wrapped in acquisition, but the request variable is
        provided so it is possible to access the REQUEST object.
        '''

    # getSkinSelections__roles__ = None  # Public
    def getSkinSelections():
        '''
        Returns the sorted list of available skin names.
        '''
