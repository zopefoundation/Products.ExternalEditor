Zope Content Management Framework (CMF) README

  What is the CMF?

    The Zope Content Management Framework provides a set of
    services and content objects useful for building highly
    dynamic, content-oriented portal sites.  As packaged, the
    CMF generates a site much like the Zope.org site.  The CMF is
    intended to be easily customizable, in terms of both the
    types of content used and the policies and services it
    provides.

  Resources

    * The CMF "dogbowl" site, http://cmf.zope.org.

    * The mailing list, zope-ptk@zope.org.  List information and
      online signup are available at:
      http://lists.zope.org/mailman/listinfo/zope-ptk.  Archives
      of the list are at: http://lists.zope.org/pipermail/zope-ptk.

  Known Issues

    Please see the separate "issues list":ISSUES.txt.

  Installation

    Requirements

      - Zope v. 2.3.1b1 or later OR
      
      - Zope 2.3.0 with Jeffrey Shell's "security info patch",
          http://cmf.zope.org/Members/jshell/security_info.patch 

    Assumptions

      - New installation

      - Zope configured using INSTANCE_HOME, '/var/zope', and
        SOFTWARE_HOME, '/usr/local/zope/Zope-2.3.1b1'.

    Procedure

      1. Unpack the 'CMF-1.0.tar.gz' tarball into a working
         directory.  For instance:

           $ cd /usr/local/zope
           $ tar xzf /tmp/CMF-1.0.tar.gz

      2. Link (or copy/move) the three CMF packages into
         '$INSTANCE_HOME/Products'.  For instance:

           $ cd /var/zope/Products
           $ ln -s /usr/local/zope/CMF-1.0beta/* .
 
      3. Restart Zope;  verify that the three CMF products loaded
         property, by examining them in 'Control_Panel/Product'.

      4. Create a 'CMF Site' object.  Join, and begin adding
         content.  Enjoy!
