CMFSetup Product README

  Overview

    This product provides a mini-framework for expressing the configured
    state of a CMF Site as a set of filesystem artifacts.  These artifacts
    consist of declarative XML files, which spell out the configuration
    settings for each tool, and supporting scripts / templates, in their
    "canonical" filesystem representations.

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

  Extending The Tool

    Third-party products extend the tool by registering handlers for
    import / export of their unique tools.
