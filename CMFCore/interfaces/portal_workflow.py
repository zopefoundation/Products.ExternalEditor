##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

"""Workflow tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]


from Interface import Attribute, Base

class portal_workflow(Base):
    '''This tool accesses and changes the workflow state of content.
    '''
    id = Attribute('id', 'Must be set to "portal_workflow"')

    # security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor(ob):
        '''
        Invoked by portal_catalog.  Allows workflows
        to add variables to the catalog based on workflow status,
        making it possible to implement queues.
        Returns a mapping containing the catalog variables
        that apply to ob.
        '''

    # security.declarePrivate('listActions')
    def listActions(info):
        '''
        Invoked by the portal_actions tool.  Allows workflows to
        include actions to be displayed in the actions box.
        Object actions are supplied by workflows that apply
        to the object.  Global actions are supplied by all
        workflows.
        Returns the actions to be displayed to the user.
        '''

    # security.declarePublic('doActionFor')
    def doActionFor(ob, action, wf_id=None, *args, **kw):
        '''
        Invoked by user interface code.
        Allows the user to request a workflow action.  The workflow object
        must perform its own security checks.
        '''

    # security.declarePublic('getInfoFor')
    def getInfoFor(ob, name, default, wf_id=None, *args, **kw):
        '''
        Invoked by user interface code.  Allows the user to request
        information provided by the workflow.  The workflow object
        must perform its own security checks.
        '''

    # security.declarePrivate('notifyCreated')
    def notifyCreated(ob):
        '''
        Notifies all applicable workflows after an object has been created
        and put in its new place.
        '''

    # security.declarePrivate('notifyBefore')
    def notifyBefore(ob, action):
        '''
        Notifies all applicable workflows of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''

    # security.declarePrivate('notifySuccess')
    def notifySuccess(ob, action, result=None):
        '''
        Notifies all applicable workflows that an action has taken place.
        '''

    # security.declarePrivate('notifyException')
    def notifyException(ob, action, exc):
        '''
        Notifies all applicable workflows that an action failed.
        '''

    # security.declarePrivate('getHistoryOf')
    def getHistoryOf(wf_id, ob):
        '''
        Invoked by workflow definitions.  Returns the history
        of an object.
        '''

    # security.declarePrivate('getStatusOf')
    def getStatusOf(wf_id, ob):
        '''
        Invoked by workflow definitions.  Returns the last element of a
        history.
        '''

    # security.declarePrivate('setStatusOf')
    def setStatusOf(wf_id, ob, status):
        '''
        Invoked by workflow definitions.  Appends to the workflow history.
        '''


class WorkflowDefinition(Base):
    '''The interface expected of workflow definitions objects.
    Accesses and changes the workflow state of objects.
    '''

    # security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor(ob):
        '''
        Invoked by the portal_workflow tool.
        Allows this workflow to make workflow-specific variables
        available to the catalog, making it possible to implement
        queues in a simple way.
        Returns a mapping containing the catalog variables
        that apply to ob.
        '''

    # security.declarePrivate('listObjectActions')
    def listObjectActions(info):
        '''
        Invoked by the portal_workflow tool.
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called only when this workflow is applicable to
        info.content.
        Returns the actions to be displayed to the user.
        '''

    # security.declarePrivate('listGlobalActions')
    def listGlobalActions(info):
        '''
        Invoked by the portal_workflow tool.
        Allows this workflow to
        include actions to be displayed in the actions box.
        Generally called on every request!
        Returns the actions to be displayed to the user.
        '''

    # security.declarePrivate('isActionSupported')
    def isActionSupported(ob, action):
        '''
        Invoked by the portal_workflow tool.
        Returns a true value if the given action name is supported.
        '''

    # security.declarePrivate('doActionFor')
    def doActionFor(ob, action, *args, **kw):
        '''
        Invoked by the portal_workflow tool.
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''

    # security.declarePrivate('isInfoSupported')
    def isInfoSupported(ob, name):
        '''
        Invoked by the portal_workflow tool.
        Returns a true value if the given info name is supported.
        '''

    # security.declarePrivate('getInfoFor')
    def getInfoFor(ob, name, default, *args, **kw):
        '''
        Invoked by the portal_workflow tool.
        Allows the user to request information provided by the
        workflow.  This method must perform its own security checks.
        '''

    # security.declarePrivate('notifyCreated')
    def notifyCreated(ob):
        '''
        Invoked by the portal_workflow tool.
        Notifies this workflow after an object has been created
        and put in its new place.
        '''

    # security.declarePrivate('notifyBefore')
    def notifyBefore(ob, action):
        '''
        Invoked by the portal_workflow tool.
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''

    # security.declarePrivate('notifySuccess')
    def notifySuccess(ob, action, result):
        '''
        Invoked by the portal_workflow tool.
        Notifies this workflow that an action has taken place.
        '''

    # security.declarePrivate('notifyException')
    def notifyException(ob, action, exc):
        '''
        Invoked by the portal_workflow tool.
        Notifies this workflow that an action failed.
        '''

    #security.declarePrivate('updateRoleMappingsFor')
    def updateRoleMappingsFor(ob):
        '''
        Updates the object permissions according to the current
        workflow state.
        '''
