""" CMFSetup product initialization

$Id$
"""

#
#   Export API for third-party products (XXX: not yet!)
#
#from SiteConfiguration import registerSetupStep
#from SiteConfiguration import registerExportScript


def initialize(context):

    return # XXX comment out the rest

    from SiteConfiguration import SiteConfigurationTool
    from SiteConfiguration import addConfiguredSiteForm
    from SiteConfiguration import addConfiguredSite
    from SiteConfiguration import listPaths

    TOOLS_AND_ICONS = ( (SiteConfigurationTool, 'www/tool.png'),)

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

    from Products.CMFCore.utils import ToolInit, registerIcon
    from Products.CMFCore.utils import ContentInit

    ToolInit( 'CMFSetup Tools'
            , tools=[ x[ 0 ] for x in TOOLS_AND_ICONS ]
            , product_name='Setup'
            , icon=None
            ).initialize( context )

    for tool, icon in TOOLS_AND_ICONS:
        registerIcon( tool, icon, globals() )


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

    from ActionsConfig import configureToolGeneratedActions
    from ActionsConfig import exportToolGeneratedActions

    registerSetupStep('configureToolGeneratedActions', '2004/05/10-01',
                      configureToolGeneratedActions)
    registerExportScript('exportToolGeneratedActions',
                         exportToolGeneratedActions)

    from ContentTypesConfig import installTypes, exportTypes
    registerSetupStep('installTypes', '2004/05/10-01', installTypes)
    registerExportScript('exportTypes', exportTypes)

    from ActionIconsConfig import configureActionIcons, exportActionIcons
    registerSetupStep('configureActionIcons', '2004/05/10-02',
                      configureActionIcons, ('installTools',))
    registerExportScript('exportActionIcons', exportActionIcons)

    from SkinsConfig import configureSkins, exportSkins
    registerSetupStep('configureSkins', '2004/05/10-01', configureSkins)
    registerExportScript('exportSkins', exportSkins)

    from WorkflowConfig import configureWorkflows, exportWorkflows
    registerSetupStep('configureWorkflows', '2004/05/10-01',
                      configureWorkflows, ('installTypes',))
    registerExportScript('exportWorkflows', exportWorkflows)

    from RolesPermissionsConfig import configureRolesPermissions
    from RolesPermissionsConfig import exportRolesPermissions
    registerSetupStep('configureRolesPermissions', '2004/05/10-01',
                      configureRolesPermissions)
    registerExportScript('exportRolesPermissions', exportRolesPermissions)

    from MembershipConfig import installMembershipToolContent
    from MembershipConfig import exportMembershipToolContent
    registerSetupStep('installMembershipToolContent', '2004/05/10-01',
                      installMembershipToolContent, ('installTools',
                                                     'installTypes'))
    registerExportScript('exportMembershipToolContent',
                         exportMembershipToolContent)

    from RemoveTools import removeInstalledTools
    registerSetupStep('removeInstalledTools', '2004/05/10-1',
                      removeInstalledTools, ('installTools',))

    from MemberDataConfig import configureMemberDataTool
    from MemberDataConfig import exportMemberDataToolConfig
    registerSetupStep('configureMemberDataTool', '2004/05/10-01',
                      configureMemberDataTool, ())
    registerExportScript('exportMemberDataToolConfig',
                         exportMemberDataToolConfig)
