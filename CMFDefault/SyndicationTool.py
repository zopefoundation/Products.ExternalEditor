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

"""CMFDefault portal_syndication tool.
"""


import os
from Products.CMFCore.utils import UniqueObject, _checkPermission
from OFS.SimpleItem import SimpleItem
from Globals import HTMLFile, package_home, InitializeClass 
import string
from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, SecurityManagement
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import ManageProperties
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
import Products.CMFCore.CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from SyndicationInfo import SyndicationInformation

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

class SyndicationTool (UniqueObject, SimpleItem):
    id = 'portal_syndication'
    meta_type = 'Default Syndication Tool'

    security = ClassSecurityInfo()
    
    #Default Sitewide Values
    isAllowed = 0
    syUpdatePeriod = 'daily'
    syUpdateFrequency = 1
    syUpdateBase = DateTime()
    max_items = 15

    #ZMI Methods
    manage_options = (({'label'     :  'Overview'
                        ,'action'   :  'overview'
                        , 'help'    :  ('CMFDefault', 'Syndication-Tool_Overview.stx') }
                        ,{'label'   :  'Properties'
                        ,'action'   :  'propertiesForm'
                        , 'help'    :   ('CMFDefault', 'Syndication-Tool_Properties.stx')}
                        ,{'label'   :  'Policies'
                        ,'action'   :  'policiesForm'
                        , 'help'    :   ('CMFDefault', 'Syndication-Tool_Policies.stx')}
                        ,{'label'   :  'Reports'
                        ,'action'   :  'reportForm'
                        , 'help'    :   ('CMFDefault', 'Syndication-Tool_Reporting.stx')}
                     ))
    security.declareProtected(ManagePortal, 'overview')
    overview = HTMLFile('synOverview', _dtmldir)
    security.declareProtected(ManagePortal, \
                              'propertiesForm')
    propertiesForm = HTMLFile('synProps', _dtmldir)
    security.declareProtected(ManagePortal, 'policiesForm')
    policiesForm = HTMLFile('synPolicies', _dtmldir)
    security.declareProtected(ManagePortal, 'reportForm')
    reportForm = HTMLFile('synReports', _dtmldir)
   
    security.declareProtected(ManagePortal, 'editProperties')
    def editProperties(self
                       , updatePeriod=None
                       , updateFrequency=None
                       , updateBase=None
                       , isAllowed=None
                       , max_items=None
                       , REQUEST=None
                      ):
        """
        Edit the properties for the SystemWide defaults on the SyndicationTool.
        """
        if isAllowed is not None:
            self.isAllowed = isAllowed
        if updatePeriod:
            self.syUpdatePeriod = updatePeriod
        else:
            try: del self.syUpdatePeriod
            except KeyError: pass
        if updateFrequency:
            self.syUpdateFrequency = updateFrequency
        else:
            try: del self.syUpdateFrequency
            except KeyError: pass
        if updateBase:
            if type( updateBase ) is type( '' ):
                updateBase = DateTime( updateBase )
            self.syUpdateBase = updateBase
        else:
            try: del self.syUpdateBase
            except KeyError: pass
        if max_items:
            self.max_items = max_items
        else:
            try: del self.max_items
            except KeyError: pass
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()
                                + '/propertiesForm'
                                +
                                '?manage_tabs_message=Tool+Updated.'
                                )

    security.declarePublic( 'editSyInformationProperties' )
    def editSyInformationProperties(self, obj
                                   , updatePeriod=None
                                   , updateFrequency=None
                                   , updateBase=None
                                   , max_items=None
                                   , REQUEST=None
                                   ):
        """
        Edit syndication properties for the obj being passed in.
        These are held on the syndication_information object.
        Not Sitewide Properties.
        """
        mgr = SecurityManagement.getSecurityManager()
        if not _checkPermission( ManageProperties, obj ):
            raise Unauthorized
        #import pdb; pdb.set_trace()
        syInfo = getattr(obj, 'syndication_information',
                         None)
        if syInfo is None:
            raise 'Syndication is Disabled'
        if updatePeriod:
            syInfo.syUpdatePeriod = updatePeriod
        else:
            syInfo.syUpdatePeriod = self.syUpdatePeriod
        if updateFrequency:
            syInfo.syUpdateFrequency = updateFrequency
        else:
            syInfo.syUpdateFrequency = self.syUpdateFrequency
        if updateBase:
            syInfo.syUpdateBase = updateBase
        else:
            syInfo.syUpdateBase = self.syUpdateBase
        if max_items:
            syInfo.max_items = max_items
        else:
            syInfo.max_items = self.max_items

    security.declarePublic('enableSyndication')
    def enableSyndication(self, obj):
        """
        Enable syndication for the obj
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is Disabled'
        else:
            if hasattr(obj, 'syndication_information'):
             raise 'Syndication Information Exists'
            syInfo = SyndicationInformation()
            obj._setObject('syndication_information', syInfo)
            syInfo=obj._getOb('syndication_information')
            syInfo.syUpdatePeriod = self.syUpdatePeriod
            syInfo.syUpdateFrequency = self.syUpdateFrequency
            syInfo.syUpdateBase = self.syUpdateBase
            syInfo.max_items = self.max_items
            syInfo.description = "Channel Description"

    security.declarePublic('disableSyndication')
    def disableSyndication(self, obj):
        """
        Disable syndication for the obj; and remove it.
        """
        syInfo = getattr(obj, 'syndication_information',
                         None)
        if syInfo is not None:
            obj._delObject('syndication_information')
        else:
            raise 'This object does not have Syndication Information'

    security.declarePublic('getSyndicatableContent')
    def getSyndicatableContent(self, obj):
        """
        An interface for allowing folderish items to implement an equivalent of PortalFolder.contentValues()
        """
        if hasattr(obj, 'synContentValues'):
            values = obj.synContentValues(obj)
        else:
            values = PortalFolder.contentValues(obj)
        return values
    security.declarePublic('buildUpdatePeriods')
    def buildUpdatePeriods(self):
        """
        Return a list of possible update periods for the xmlns: sy
        """
        updatePeriods = (('hourly', 'Hourly'), ('daily', 'Daily'),
                        ('weekly', 'Weekly'), ('monthly',
                        'Monthly'), ('yearly', 'Yearly'))
        return updatePeriods

    security.declarePublic('isSiteSyndicationAllowed')
    def isSiteSyndicationAllowed(self):
        """
        Return sitewide syndication policy
        """
        return self.isAllowed

    security.declarePublic('isSyndicationAllowed')
    def isSyndicationAllowed(self, obj=None):
        """
        Check whether syndication is enabled for the site.  This
        provides for extending the method to check for whether a
        particular obj is enabled, allowing for turning on only
        specific folders for syndication.
        """
        syInfo = getattr(obj, 'syndication_information',
                         None)
        if syInfo is None:
            return 0
        else:
            return self.isSiteSyndicationAllowed()

    security.declarePublic('getUpdatePeriod')
    def getUpdatePeriod( self, obj=None ):
        """
        Return the update period for the RSS syn namespace.
        This is either on the object being passed or the
        portal_syndication tool (if a sitewide value or default is set)

        NOTE:  Need to add checks for sitewide policies!!!
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is Not Allowed'
        else:
            syInfo = getattr(obj, 'syndication_information',
                             None)
            if syInfo is not None:
                return syInfo.syUpdatePeriod
            else:
                #return self.syUpdatePeriod
                return 'Syndication is Not Allowed'
    
    security.declarePublic('getUpdateFrequency')
    def getUpdateFrequency(self, obj=None):
        """
        Return the update frequency (as a positive integer) for
        the syn namespace.  This is either on the object being
        pass or the portal_syndication tool (if a sitewide value
        or default is set).

        Note:  Need to add checks for sitewide policies!!!
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'
        else:
            syInfo = getattr(obj, 'syndication_information',
                             None)
            if syInfo is not None:
                return syInfo.syUpdateFrequency
            else:
                return 'Syndication is not Allowed'
     
    security.declarePublic('getUpdateBase')
    def getUpdateBase(self, obj=None):
        """
        Return the base date to be used with the update frequency
        and the update period to calculate a publishing schedule.
        
        Note:  I'm not sure what's best here, creation date, last
        modified date (of the folder being syndicated) or some
        arbitrary date.  For now, I'm going to build a updateBase
        time from zopetime and reformat it to meet the W3CDTF.
        Additionally, sitewide policy checks might have a place
        here...
        """
        #import pdb; pdb.set_trace()
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'
        else:
            syInfo = getattr(obj, 'syndication_information',
                               None)
            if syInfo is not None:
                 when = syInfo.syUpdateBase
                 return when.ISO()
            else:
                return 'Syndication is not Allowed'

    security.declarePublic('getHTML4UpdateBase')
    def getHTML4UpdateBase(self, obj):
        """
        Return HTML4 formated UpdateBase DateTime
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'
        else:
            syInfo = getattr(obj, 'syndication_information',
                                None)
            if syInfo is not None:
                when = syInfo.syUpdateBase
                return when.HTML4()
            else:
                return 'Syndication is not Allowed'

    def getMaxItems(self, obj=None):
        """
        Return the max_items to be displayed in the syndication
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'
        else:
            syInfo = getattr(obj, 'syndication_information',
                                None)
            if syInfo is not None:
                return syInfo.max_items
            else:
                return 'Syndication is not Allowed'

InitializeClass(SyndicationTool)
