CMF Hotfix Release, 2003/09/08

  Overview

    This hotfix product remedies a gap in the permissions assigned to
    "action providers" in the Zope CMF.  Sites which dynamically compute
    navigation using such actions are vulnerable to having actions
    added or removed by a sufficiently clever cracker.

  Affected Versions

    Users of CMF version 1.4 are potentially affected by this issue,
    as are users of version 1.3.1 and earlier.  Versions 1.3.2 and 1.4.1
    already contain this fix, and do not require this hotfix.

  Installing the Hotfix

    1. Unpack the tarball into a working directory, and then move or link
       the 'CMFHotfix_20030908' directory into the Products directory of
       your '$INSTANCE_HOME' (next to 'CMFCore', 'CMFDefault', etc.).
       
    2. Restart Zope.
    
    E.g., assuming that you have Zope installed in '/usr/lib/Zope-2.6.1'
    (the '$SOFTWARE_HOME'), and that your instance data is in
    '/var/zope/instance' (the '$INSTANCE_HOME')::

      $ cd /var/zope/instance/Products
      $ tar xzf /tmp/CMFHotfix_20030908.tar.gz
      $ cd /var/zope/instance
      $ kill -HUP `cat var/Z2.pid`

    Windows users should unzip the ZIP file and move the extracted
    'CMFHotfix_20030908' folder to their Zope's 'Products' folder.
 
  Uninstalling the Hotfix
  
    You may remove the 'CMFHotfix_20030908' product directory after upgrading
    to one of the updated versions of CMF (1.3.2, 1.4.1, or later).  E.g.::

      $ cd /var/zope/instance/Products
      $ rm -r CMFHotfix_20030908

