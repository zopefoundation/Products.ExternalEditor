##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
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
