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

      - (x) removal / creation of specified tools

      - (x) itself :)

      - (x) the role / permission map on the site object

      - (x) properties of the site object

      - (x) 'portal_actions'
            (Products.CMFCore.ActionsTool.ActionsTool)

            o action providers, and their actions; note that this removes
              the requirement to have individual tools configure their own
              actions

      - (x) 'portal_skins'

            o tool properties

            o FilesystemDirectoryView instances

            o skin path definitions

      - (x) 'portal_types'

            o content type definitions, including actions

      - (x) 'portal_workflow'

            o bindings of workflows to content types

            o DCWorkflow definitions, including supporting scripts

      - (_) 'portal_catalog'
            (Products.CMFCore.CatalogTool.CatalogTool)

            o index names / types

            o metadata column names

      - (_) 'portal_membership'

            o "skeleton" home folder (XXX: is this in the core?)

      - (_) 'portal_memberdata'

            o member properties

      - (_) 'content_type_registry'

            o predicate -> portal_type bindings.

      - (_) 'caching_policy_manager'

            o policy settings

      - (_) 'portal_metadata'

            o global properties

            o default element policies

            o type-specific element policies

      - (_) 'portal_actionicons'
            (Products.CMFActionIcons.ActionIconsTool.ActionIconsTool)

            o action title / icon bindings

      - (_) 'cookie_authentication'

            o tool properties

      - (_) 'MailHost'

            o tool properties

      - (_) user folder configuration

      - (_) folder structure

  TODO

      - (x) Display / download diffs between configurations (profiles
            and shapshots) Done 2004/07/20, TS.

      - (x) Modify profile selection to use a drop-down list of registered
            profiles.

      - (x) Allow import from snapshots.

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
