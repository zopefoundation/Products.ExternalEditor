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
""" Skins tool interface description.

$Id$
"""

from Interface import Attribute, Base

class portal_skins(Base):
    '''An object that provides skins to a portal object.
    '''
    id = Attribute('id', 'Must be set to "portal_skins"')

    # Private
    def getSkinPath(name):
        """Converts a skin name to a skin path.
        """

    # Public
    def getDefaultSkin():
        """Returns the default skin name.
        """

    # Public
    def getRequestVarname():
        """Returns the variable name to look for in the REQUEST.
        """

    # Private
    def getSkinByPath(path, raise_exc=0):
        """Returns a skin at the given path.

        A skin path is of the format:
        'some/path, some/other/path, ...'  The first part has precedence.

        A skin is a specially wrapped object that looks through the layers
        in the correct order.
        """

    # Private
    def getSkinByName(name):
        """Returns the named skin.
        """

    # Public
    def getSkinSelections():
        """Returns the sorted list of available skin names.
        """
