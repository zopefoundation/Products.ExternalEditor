##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################

# Zope External Editor Product by Casey Duncan

from Globals import ImageFile, DTMLFile
from OFS.ObjectManager import ObjectManager
from OFS.Application import Application
from ExternalEditor import ExternalEditor

# Add the icon and the edit method to the misc_ namespace

misc_ = {'edit_icon': ImageFile('edit_icon.gif', globals())}

# Monkey patch in our manage_main for Object Manager

ObjectManager.manage_main = DTMLFile('manage_main', globals())

# Monkey patch the application object
exedit = Application.externalEdit_ = ExternalEditor()

def initialize(context):
    # Compensate for past inadequacies
    app = context._ProductContext__app
    if app.externalEdit_ is not exedit and \
       app.externalEdit_.__class__  is ExternalEditor:
        try:
            del app.externalEdit_
        except:
            pass
