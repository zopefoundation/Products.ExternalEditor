CMF Hotfix Release, 2003/10/26

  Overview

    This hotfix product addresses two issues with the Zope Content
    Management Framework (CMF):
    
     - It changes the permission assigned to the 'searchMembers'
       method of the 'portal_membership' tool.  This method exposes user
       IDs and other information about site members, and could be used by a 
       sufficiently clever cracker to mount an attack on the site.

     - It patches the 'registeredNotify' method of the 'portal_registration'
       tool, removing the possibility that an attacker might inject a
       hostile e-mail address into the mail which it generates.
    
    Zope Corporation recommends that all CMF-based sites upgrade to a version
    (see below) which contains the fix for this issue.  Sites which for some
    reason cannot upgrade may instead install this hotfix product.

  Affected Versions

    Users of CMF version 1.4.1 are potentially affected by this issue,
    as are users of version 1.3.2 and earlier.  Versions 1.3.3 and 1.4.2
    will contain this fix, and therefore will not require this hotfix.

  Obtaining the Hotfix

    The hotfix is available in two formats:

    - As a "Unix tarball",
      http://cmf.zope.org/download/CMFHotfix_20031026/CMFHotfix_20031026.tar.gz

    - As a "Windows zipfile",
      http://cmf.zope.org/download/CMFHotfix_20031026/CMFHotfix_20031026.zip

  Installing the Hotfix

    1. Unpack the tarball into a working directory, and then move or link
       the 'CMFHotfix_20031026' directory into the Products directory of
       your '$INSTANCE_HOME' (next to 'CMFCore', 'CMFDefault', etc.).
       
    2. Restart Zope.
    
    E.g., assuming that you have Zope installed in '/usr/lib/Zope-2.6.1'
    (the '$SOFTWARE_HOME'), and that your instance data is in
    '/var/zope/instance' (the '$INSTANCE_HOME')::

      $ cd /var/zope/instance/Products
      $ tar xzf /tmp/CMFHotfix_20031026.tar.gz
      $ cd /var/zope/instance
      $ kill -HUP `cat var/Z2.pid`

    Windows users should unzip the ZIP file and move the extracted
    'CMFHotfix_20031026' folder to their Zope's 'Products' folder.
 
  Uninstalling the Hotfix
  
    You may remove the 'CMFHotfix_20031026' product directory after upgrading
    to one of the updated versions of CMF (1.3.3, 1.4.2, or later).  E.g.::

      $ cd /var/zope/instance/Products
      $ rm -r CMFHotfix_20031026

