CMFSetup Product README

  Overview

    This product provides a mini-framework for expressing the configured
    state of a CMF Site as a set of filesystem artifacts.  These artifacts
    consist of declarative XML files, which spell out the configuration
    settings for each tool, and supporting scripts / templates, in their
    "canonical" filesystem representations.

  Configurations Included

    The 'portal_setup' tool knows how to export / import configurations
    and scripts for the following tools:

      - itself :)

      - the role / permission map on the site object

      - removal / creation of specified tools

      - cookie crumbler configuration

      - folder structure

      - 'portal_actionicons'
        (Products.CMFActionIcons.ActionIconsTool.ActionIconsTool)

        o action title / icon bindings

      - 'portal_actions'
        (Products.CMFCore.ActionsTool.ActionsTool)
 
        o action providers, and their actions; note that this removes
          the requirement to have individual tools configure their own
          actions

      - 'portal_catalogs'
        (Products.CMFCore.CatalogTool.CatalogTool)

        o index names / types
        
        o metadata column names

      - 'portal_membership'

        o "skeleton" home folder (XXX: is this in the core?)

      - 'portal_memberdata'

        o member properties

      - 'portal_skins'

        o FilesystemDirectoryView instances

        o skin path definitions

      - 'portal_types'

        o content type definitions, including actions

      - 'portal_workflow'

        o bindings of workflows to content types

        o DCWorkflow definitions, including supporting scripts

  Extending The Tool

    Third-party products extend the tool by registering handlers for
    import / export of their unique tools.

  Glossary

    Site -- 
      The instance in the Zope URL space which defines a "zone of service"
      for a set of CMF tools.

    Profile --
      A "preset" configuration of a site, defined on the filesystem

    Snapshot --
      "Frozen" site configuration, captured within the setup tool

    "dotted name" --
      The Pythonic representation of the "path" to a given function /
      module, e.g. 'Products.CMFCore.utils.getToolByName'.
