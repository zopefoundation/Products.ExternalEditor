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

"""Discussion tool interface description.
$Id$
"""
__version__='$Revision$'[11:-2]


from Interface import Attribute, Base

class portal_discussion(Base):
    '''Links content to discussions.
    '''
    id = Attribute('id', 'Must be set to "portal_discussion"')

    #getDiscussionFor__roles__ = None
    def getDiscussionFor(content):
        '''Gets the PortalDiscussion object that applies to content.
        '''

    #isDiscussionAllowedFor__roles__ = None
    def isDiscussionAllowedFor(content):
        '''Returns a boolean indicating whether a discussion is
        allowed for the specified content.
        '''
