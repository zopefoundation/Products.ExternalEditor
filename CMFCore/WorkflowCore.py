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

"""Common pieces of the workflow architecture.
$Id$
"""
__version__='$Revision$'[11:-2]

from MethodObject import Method
from utils import getToolByName
import sys


class WorkflowException (Exception):
    '''
    Exception while invoking workflow.
    '''


class ObjectDeleted (Exception):
    '''
    Raised to tell the workflow tool that the object has been deleted.
    Swallowed by the workflow tool.
    '''
    def __init__(self, result=None):
        self._r = result

    def getResult(self):
        return self._r


class ObjectMoved (Exception):
    '''
    Raised to tell the workflow tool that the object has moved.
    Swallowed by the workflow tool.
    '''
    def __init__(self, new_ob, result=None):
        self._ob = new_ob  # Includes acquisition wrappers.
        self._r = result

    def getResult(self):
        return self._r

    def getNewObject(self):
        return self._ob


class WorkflowMethod (Method):
    '''
    Wraps a method to workflow-enable it.
    '''
    _need__name__=1

    def __init__(self, method, id=None, reindex=1):
        self._m = method
        if id is None:
            id = method.__name__
        self._id = id
        # reindex ignored since workflows now perform the reindexing.

    def __call__(self, instance, *args, **kw):
        '''
        Invokes the method.
        '''
        wf = getToolByName(instance, 'portal_workflow', None)
        if wf is None or not hasattr(wf, 'wrapWorkflowMethod'):
            # No workflow tool found.
            try:
                res = apply(self._m, (instance,) + args, kw)
            except ObjectDeleted, ex:
                res = ex.getResult()
            else:
                catalog = getToolByName(instance, 'portal_catalog', None)
                if catalog is not None:
                    catalog.reindexObject(ob)
        else:
            res = wf.wrapWorkflowMethod(instance, self._id, self._m,
                                        (instance,) + args, kw)
        return res

# Backward compatibility.
WorkflowAction = WorkflowMethod
