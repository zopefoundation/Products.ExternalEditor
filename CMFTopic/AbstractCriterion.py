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
Home of the abstract Criterion base class.
"""
from OFS.SimpleItem import Item
from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
import string, operator

from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from TopicPermissions import ChangeTopics

class AbstractCriterion(Persistent, Item, Implicit):
    """ Abstract base class for Criterion objects. """

    security = ClassSecurityInfo()

    security.declareProtected(ChangeTopics, 'apply')
    def apply(self, command):
        """\
        command is expected to be a dictionary.  It gets applied
        to self.edit, and exists to make using Python Scripts
        easier.
        """
        apply(self.edit, (), command)

    security.declareProtected(ChangeTopics, 'editableAttributes')
    def editableAttributes(self):
        """\
        Return a list of editable attributes, used by topics
        to build commands to send to the 'edit' command of each
        criterion, which may vary.

        Requires concrete subclasses to implement the attribute
        '_editableAttributes' which is a tuple of attributes
        that can be edited, for example:

          _editableAttributes = ('value', 'direction',)
        """
        return self._editableAttributes

    security.declareProtected(AccessContentsInformation, 'Type')
    def Type(self):
        """\
        Return the Type of Criterion this object is.  This
        method can be overriden in subclasses, or those
        concrete subclasses must define the 'meta_type'
        attribute.
        """
        return self.meta_type
    
    security.declareProtected(AccessContentsInformation, 'Field')
    def Field(self):
        """\
        Return the field that this criterion searches on.  The
        concrete subclasses can override this method, or have
        the 'field' attribute.
        """
        return self.field

    security.declareProtected(AccessContentsInformation, 'Description')
    def Description(self):
        """\
        Return a brief but helpful description of the Criterion type,
        preferably based on the classes __doc__ string.
        """
        strip = string.strip
        split = string.split
        
        return string.join(             # Sew a string together after we:
            filter(operator.truth,      # Filter out empty lines
                   map(strip,           # strip whitespace off each line
                       split(self.__doc__, '\n') # from the classes doc string
                       )
                   )
            )

InitializeClass(AbstractCriterion)

        
