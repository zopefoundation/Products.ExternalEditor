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
"""External Editor Photoshop Plugin

$Id$
"""

# Note that Photoshop's com API is not terribly rich and external editor
# cannot discern from it when a Photoshop file has been closed.
# Therefore Photoshop should probably be used without DAV locks or
# with always_borrow_locks enabled

from time import sleep
import win32com
from win32com import client # Initialize Client module

class EditorProcess:
    def __init__(self, file):
        """Launch editor process"""
        ps = win32com.client.Dispatch('Photoshop.Application')
        # Try to open the file, keep retrying until we succeed or timeout
        i = 0
        timeout = 45
        while i < timeout:
            try:
                fileconn = ps.Open(file)
            except:
                i += 1
                if i >= timeout:
                    raise RuntimeError('Could not launch Photoshop.')
                sleep(1)
            else:
                break
        self.fileconn = fileconn
        self.file = file
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        sleep(timeout)
            
    def isAlive(self):
        """Returns true if the editor process is still alive"""
        # Photoshop has no API for checking if a file is still open
        # This workaround just checks if the file connection is
        # still accessible. It will be until Photoshop itself is closed 8^/
        try:
            self.fileconn.Title # See if the file is still accessible
        except:
            return 0
        return 1

def test():
    print 'Connecting to Photoshop...'
    f = EditorProcess('C:\\Windows\\Cloud.gif')
    print ('%s is open...' % f.fileconn.Title),
    if f.isAlive():
        print 'yes'
        print 'Test Passed.'
    else:
        print 'no'
        print 'Test Failed.'
    
if __name__ == '__main__':
    test()
