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

"""Registration tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]


from Interface import Attribute, Base

class portal_registration(Base):
    '''Establishes policies for member registration. Depends on
    portal_membership. Is not aware of membership storage details.
    '''
    id = Attribute('id', 'Must be set to "portal_registration"')

    #isRegistrationAllowed__roles__ = None  # Anonymous permission
    def isRegistrationAllowed(REQUEST):
        '''Returns a boolean value indicating whether the user
        is allowed to add a member to the portal.
        '''

    #testPasswordValidity__roles__ = None  # Anonymous permission
    def testPasswordValidity(password, confirm=None):
        '''If the password is valid, returns None.  If not, returns
        a string explaining why.
        '''

    #testPropertiesValidity__roles__ = None  # Anonymous permission
    def testPropertiesValidity(new_properties, member=None):
        '''If the properties are valid, returns None.  If not, returns
        a string explaining why.
        '''

    #generatePassword__roles__ = None  # Anonymous permission
    def generatePassword():
        '''Generates a password which is guaranteed to comply
        with the password policy.
        '''

    # permission: 'Add portal member'
    def addMember(id, password, roles=('Member',), domains='',
                  properties=None):
        '''Creates a PortalMember and returns it. The properties argument
        can be a mapping with additional member properties. Raises an
        exception if the given id already exists, the password does not
        comply with the policy in effect, or the authenticated user is not
        allowed to grant one of the roles listed (where Member is a special
        role that can always be granted); these conditions should be
        detected before the fact so that a cleaner message can be printed.
        '''

    # permission: 'Add portal member'
    def isMemberIdAllowed(id):
        '''Returns 1 if the ID is not in use and is not reserved.
        '''

    #afterAdd__roles__ = ()  # No permission.
    def afterAdd(member, id, password, properties):
        '''Called by portal_registration.addMember()
        after a member has been added successfully.'''

    # permission: 'Mail forgotten password'
    def mailPassword(forgotten_userid, REQUEST):
        '''Email a forgotten password to a member.  Raises an exception
        if user ID is not found.
        '''

    # permission: 'Set own password'
    def setPassword(password, domains=None):
        '''Allows the authenticated member to set his/her own password.
        '''
            
    # permission: 'Set own properties'
    def setProperties(properties=None, **kw):
        '''Allows the authenticated member to set his/her own properties.
        '''
