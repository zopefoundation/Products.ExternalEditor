##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" CMFSetup product initialization.

$Id$
"""

from AccessControl import ModuleSecurityInfo

from permissions import ManagePortal
from registry import _profile_registry as profile_registry

security = ModuleSecurityInfo( 'Products.CMFSetup' )
security.declareProtected( ManagePortal, 'profile_registry' )

def initialize( context ):

    from Products.CMFCore.utils import ToolInit, registerIcon
    from tool import SetupTool


    ToolInit( 'CMF Setup Tool'
            , tools=[ SetupTool ]
            , product_name='Setup'
            , icon=None
            ).initialize( context )

    registerIcon(  SetupTool, 'www/tool.png', globals() )

    from factory import addConfiguredSiteForm
    from factory import addConfiguredSite

    # Add factory for a site which follows a profile.  We specify
    # meta_type and interfaces because we don't actually register a
    # class here, only a factory.
    context.registerClass( meta_type='Configured CMF Site'
                         , constructors=( addConfiguredSiteForm
                                        , addConfiguredSite
                                        )
                         , permissions=( 'Add CMF Sites', )
                         , interfaces=None
                         )


    profile_registry.registerProfile( 'default'
                                    , 'CMFSetup Default'
                                    , 'Default profile (for testing)'
                                    , 'profiles/default'
                                    , 'CMFSetup'
                                    )

    return # XXX comment out the rest

    # XXX:  This is *all* policy, and belongs in an XML file!

    # Install setup steps and export scripts
    from SetupSteps import installTools
    from SetupSteps import configureCookieCrumbler

    registerSetupStep('installTools', '2004/05/10-01',
                    installTools)

    registerSetupStep('configureCookieCrumbler', '2004/05/10-01',
                    configureCookieCrumbler)

    from CatalogIndexesConfig import configureCatalogIndexes
    from CatalogIndexesConfig import exportCatalogIndexes

    registerSetupStep('configureCatalogIndexes', '2004/05/10-01',
                      configureCatalogIndexes, ('installTools',))
    registerExportScript('exportCatalogIndexes', exportCatalogIndexes)

    from SkeletonBuilder import buildFolderStructure
    from SkeletonBuilder import generateSkeleton

    registerSetupStep('buildFolderStructure', '2004/05/10-01',
                      buildFolderStructure, ( 'installTypes'
                                            , 'configureSkins'
                                            , 'configureWorkflows'
                                            # Because the folder buildout will
                                            # need to know whomever is the
                                            # author of certain content:
                                            , 'installMembershipToolContent'
                                            ))
    registerExportScript('generateSkeleton', generateSkeleton)

    from ActionIconsConfig import configureActionIcons, exportActionIcons
    registerSetupStep('configureActionIcons', '2004/05/10-02',
                      configureActionIcons, ('installTools',))
    registerExportScript('exportActionIcons', exportActionIcons)

    from MembershipConfig import installMembershipToolContent
    from MembershipConfig import exportMembershipToolContent
    registerSetupStep('installMembershipToolContent', '2004/05/10-01',
                      installMembershipToolContent, ('installTools',
                                                     'installTypes'))
    registerExportScript('exportMembershipToolContent',
                         exportMembershipToolContent)

    from MemberDataConfig import configureMemberDataTool
    from MemberDataConfig import exportMemberDataToolConfig
    registerSetupStep('configureMemberDataTool', '2004/05/10-01',
                      configureMemberDataTool, ())
    registerExportScript('exportMemberDataToolConfig',
                         exportMemberDataToolConfig)
