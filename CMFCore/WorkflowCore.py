##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Common pieces of the workflow architecture.

$Id$
"""

class WorkflowException( Exception ):

    """ Exception while invoking workflow.
    """


class ObjectDeleted( Exception ):

    """ Raise to tell the workflow tool that the object has been deleted.

    Swallowed by the workflow tool.
    """
    def __init__(self, result=None):
        self._r = result

    def getResult(self):
        return self._r


class ObjectMoved( Exception ):

    """ Raise to tell the workflow tool that the object has moved.

    Swallowed by the workflow tool.
    """
    def __init__(self, new_ob, result=None):
        self._ob = new_ob  # Includes acquisition wrappers.
        self._r = result

    def getResult(self):
        return self._r

    def getNewObject(self):
        return self._ob
