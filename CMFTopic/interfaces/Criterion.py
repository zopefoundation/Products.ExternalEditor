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
"""\
Declare interface for search criterion classes, as used by Topic
instances to build their queries.
"""
import Interface

class Criterion(Interface.Base):
    """\
    A Topic is composed of Criterion objects which specify the query
    used for the Topic.  By supplying some basic information, the
    Criterion objects can be plugged into Topics without the Topic
    having to be too aware of the Criteria types.
    """

    def Type(self):
        """\
        Return the type of criterion object this is (ie - 'List Criterion')
        """

    def Field(self):
        """\
        Return the field this criterion object searches on.
        """

    def Description(self):
        """\
        Return a brief description of the criteria type.
        """

    def editableAttributes(self):
        """\
        Returns a tuble of editable attributes.  The values of this
        are used by the topic to build commands to send to the
        'edit' method based on each criterion's setup.
        """

    def getEditForm(self):
        """\
        Return the name of a DTML component used to edit criterion.
        Editforms should be specific to their type of criteria.
        """

    def apply(self, command):
        """\
        To make it easier to apply values from the rather dynamic
        Criterion edit form using Python Scripts, apply takes a
        mapping object as a default and applies itself to self.edit.

        It's basically a nice and protected wrapper around
        apply(self.edit, (), command).
        """

    def edit(self, **kw):
        """\
        The signature of this method should be specific to the
        criterion.  Using the values in the attribute
        '_editableAttributes', the Topic can apply the right
        commands to each criteria object as its being edited without
        having to know too much about the structure.
        """

    def criteriaItems(self):
        """\
        Return a sequence of key-value tuples, each representing
        a value to be injected into the query dictionary (and,
        therefore, tailored to work with the catalog).
        """
