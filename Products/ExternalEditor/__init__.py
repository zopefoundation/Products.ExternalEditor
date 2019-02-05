##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# Zope External Editor Product by Casey Duncan

from App.ImageFile import ImageFile
from App.special_dtml import DTMLFile
from ExternalEditor import ExternalEditor, EditLink
from OFS.FindSupport import FindSupport
from OFS.Folder import Folder
from OFS.ObjectManager import ObjectManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Add the icon and the edit method to the misc_ namespace

misc_ = {'edit_icon': ImageFile('edit_icon.gif', globals())}

# Insert the global external editor resources
Folder.externalEdit_ = ExternalEditor()
Folder.externalEditLink_ = EditLink

# Monkey patch in our manage_main for Object Manager
ObjectManager.manage_main = PageTemplateFile('zpt/main', globals())

# Add our patch for the find results template
FindSupport.manage_findForm = DTMLFile('dtml/findForm', globals(),
                                       management_view='Find')
