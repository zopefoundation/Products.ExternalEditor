""" CMFSetup product initialization

$Id$
"""
from AccessControl import ModuleSecurityInfo

from permissions import ManagePortal
from registry import _profile_registry as profile_registry

security = ModuleSecurityInfo( 'Products.CMFSetup' )
security.declareProtected( ManagePortal, 'profile_registry' )

def initialize(context):

    from Products.CMFCore.utils import ToolInit, registerIcon
    from tool import SetupTool

    TOOLS_AND_ICONS = ( ( SetupTool, 'www/tool.png' ),)

    ToolInit( 'CMFSetup Tools'
            , tools=[ x[ 0 ] for x in TOOLS_AND_ICONS ]
            , product_name='Setup'
            , icon=None
            ).initialize( context )

    for tool, icon in TOOLS_AND_ICONS:
        registerIcon( tool, icon, globals() )

    return # XXX comment out the rest

    from SiteConfiguration import addConfiguredSiteForm
    from SiteConfiguration import addConfiguredSite
    from SiteConfiguration import listPaths

    # Add SiteConfiguration constructor.
    # We specify meta_type and interfaces because we don't actually register a
    # class here, only a constructor.
    #
    # Note that the 'listPaths' bit is a hack to get that
    # object added to the factory dispatcher, so that it will be available
    # within the 'addConfiguredSiteForm' template.
    #
    context.registerClass( meta_type='Configured CMF Site'
                         , permission='Create Configured CMF Site'
                         , constructors=( addConfiguredSiteForm
                                        , addConfiguredSite
                                        , listPaths #  WTF?
                                        )
                         , interfaces=None
                         )


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
