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
"""
Various date criterion
"""
from AccessControl import ClassSecurityInfo
from Topic import Topic
from AbstractCriterion import AbstractCriterion
from DateTime.DateTime import DateTime
import Globals, string, interfaces, operator

from Products.CMFCore import CMFCorePermissions
import TopicPermissions

class FriendlyDateCriterion(AbstractCriterion):
    """\
    Put a friendly interface on date range searches, like
    'where effective date is less than 5 days old'.
    """
    __implements__ = (interfaces.Criterion,)
    meta_type = 'Friendly Date Criterion'
    security = ClassSecurityInfo()

    _editableAttributes = ('value', 'operation', 'daterange')

    _defaultDateOptions = (
        (1, '1 Day'),
        (2, '2 Days'),
        (5, '5 Days'),
        (7, '1 Week'),
        (14, '2 Weeks'),
        (31, '1 Month'),
        (31*3, '3 Months'),
        (31*6, '6 Months'),
        (365, '1 Year'),
        (365*2, '2 years'),
        )
    def __init__(self, id, field):
        self.id, self.field = id, field
        self.value = None
        self.operation = 'min'
        self.daterange = 'old'

    security.declarePublic('defaultDateOptions')
    def defaultDateOptions(self):
        """ List of default values and labels for date options """
        return self._defaultDateOptions

    security.declareProtected(TopicPermissions.ChangeTopics, 'getEditForm')
    def getEditForm(self):
        return 'friendlydatec_editform'

    security.declareProtected(TopicPermissions.ChangeTopics, 'edit')
    def edit(self, value=None, operation='min', daterange='old'):
        """ Update the values to match against """
        if value in (None, ''):
            self.value = None
        else:
            try: self.value = int(value)
            except: raise ValueError, 'Supplied value should be an int'

        if operation in ('min','max'):
            self.operation = operation
        else:
            raise ValueError, 'Operation type not in set {min,max}'

        if daterange in ('old', 'ahead'):
            self.daterange = daterange
        else:
            raise ValueError, 'Date range not in set {old,ahead}'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """ Return items to be used to build the catalog query """
        if self.value is None: return ()
        field = self.Field()
        value = self.value

        # Negate the value for 'old' days
        if self.daterange == 'old': value = -value

        date = DateTime() + value

        result = ((field, date),
                  ('%s_usage' % field, 'range:%s' % self.operation),)

        return result

Globals.InitializeClass(FriendlyDateCriterion)

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append(FriendlyDateCriterion)
