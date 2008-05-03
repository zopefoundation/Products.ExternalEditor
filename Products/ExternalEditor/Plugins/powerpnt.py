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
"""External Editor MSPowerpoint Plugin

$Id$
"""

import os
from time import sleep
import win32com
from win32com import client # Initialize Client module

class EditorProcess:
    def __init__(self, file):
        """Launch editor process"""
        ppt = win32com.client.Dispatch('Powerpoint.Application')
        ppt.Visible = 1
        # Try to open the file, keep retrying until we succeed or timeout
        i = 0
        timeout = 45
        while i < timeout:
            try:
                ppt.Presentations.Open(file)
            except:
                raise
                i += 1
                if i >= timeout:
                    raise RuntimeError('Could not launch Powerpoint.')
                sleep(1)
            else:
                break
        self.powerpntapp = ppt
        self.file = file
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        sleep(timeout)
            
    def isAlive(self):
        """Returns true if the editor process is still alive"""
        try:
            self.powerpntapp.Presentations(self.file)
        except:
            return 0
        else:
            return 1

def test():
    import os
    from time import sleep
    from tempfile import mktemp
    fn = 'E:\Documents and Settings\Default User\Templates\powerpnt.ppt'
    print 'Connecting to Powerpoint...'
    f = EditorProcess(fn)
    print 'Attached to %s %s' % (`f.powerpntapp`, f.powerpntapp.Version)
    print ('%s is open...' % fn),
    if f.isAlive():
        print 'yes'
        print 'Test Passed.'
    else:
        print 'no'
        print 'Test Failed.'
    
if __name__ == '__main__':
    test()
