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

"""CMFDefault portal_properties tool.

$Id$
"""
__version__='$Revision$'[11:-2]


from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_inner, aq_parent

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from utils import _dtmldir


class PropertiesTool(UniqueObject, SimpleItem, ActionProviderBase):
    id = 'portal_properties'
    meta_type = 'Default Properties Tool'
    _actions = [ActionInformation(id='configPortal'
                            , title='Reconfigure Portal'
                            , description='Reconfigure the portal'
                            , action=Expression(
            text='string: ${portal_url}/reconfig_form')
                            , permissions=(CMFCorePermissions.ManagePortal,)
                            , category='global'
                            , condition=None
                            , visible=1
                             )] 

    security = ClassSecurityInfo()

    manage_options = ( ActionProviderBase.manage_options +
                      ({ 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainPropertiesTool', _dtmldir )

    #
    #   'portal_properties' interface methods
    #
    security.declarePrivate('listActions')
    def listActions(self, info=None):
        """
        Return actions provided by tool.
        """
        return self._actions

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'editProperties' )
    def editProperties(self, props):
        '''Change portal settings'''
        aq_parent(aq_inner(self)).manage_changeProperties(props)
        self.MailHost.smtp_host = props['smtp_server']
        if hasattr(self, 'propertysheets'):
            ps = self.propertysheets
            if hasattr(ps, 'props'):
                ps.props.manage_changeProperties(props)

    def title(self):
        return self.aq_inner.aq_parent.title

    def smtp_server(self):
        return self.MailHost.smtp_host


InitializeClass(PropertiesTool)
