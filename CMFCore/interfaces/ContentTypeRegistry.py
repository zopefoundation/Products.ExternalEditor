##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""
Declare interfaces for MIMEtype <-> Type object registry objects.
"""

from Interface import Attribute, Base

class ContentTypeRegistryPredicate(Base):
    """\
    Express a rule for matching a given name/typ/body.
    """

    def __call__(name, typ, body):
        """ Return true if the rule matches, else false. """

    def getTypeLabel():
        """ Return a human-readable label for the predicate type. """
    
    def edit(**kw):
        """ Update the predicate. """

    def predicateWidget():
        """\
        Return a snipped of HTML suitable for editing the
        predicate;  the snippet should arrange for values
        to be marshalled by ZPublisher as a ':record', with
        the ID of the predicate as the name of the record.
        
        The registry will call the predictate's 'edit' method,
        passing the fields of the record.
        """

class ContentTypeRegistry(Base):
    """ Registry for rules which map PUT args to a CMF Type Object. """

    def findTypeName(name, typ, body):
        """\
        Perform a lookup over a collection of rules, returning the
        the Type object corresponding to name/typ/body.  Return None
        if no match found.
        """
