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
"""External Editor MSWord Plugin

$Id$
"""

import os
from time import sleep
import win32com
import pythoncom
from win32com import client # Initialize Client module

class EditorProcess:
    def __init__(self, file):
        """Launch editor process"""
        word = win32com.client.Dispatch('Word.Application')
        # Try to open the file, keep retrying until we succeed or timeout
        i = 0
        timeout = 45
        while i < timeout:
            try:
                word.Documents.Open(file)
            except:
                i += 1
                if i >= timeout:
                    raise RuntimeError('Could not launch Word.')
                sleep(1)
            else:
                break
        word.Visible = 1
        self.wordapp = word
        self.file = file
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        sleep(timeout)
            
    def isAlive(self):
        """Returns true if the editor process is still alive"""
       	try:
            self.wordapp.Documents(self.file)
        except pythoncom.com_error, why:
            # COM will reject the call to access the doc if the user is
            # doing anything interactive at the time the call is made.  The
            # symptom is a COM error numbered -2147418111 named "Call rejected
            # by callee".  This is most critically seen when the user has
            # modified the document but chooses "exit" without first saving.
            # Without this check in place, the document is not saved back to
            # Zope, but no error is raised.
            if why[0] == -2147418111:
                return 1
        except:
            return 0
        else:
            return 1
        
def test():
    import os
    from time import sleep
    from tempfile import mktemp
    fn = mktemp('.html')
    f = open(fn, 'w')
    f.write('<html>\n  <head></head>\n'
            '<body><h1>A Test Doc</h1></body>\n</html>')
    f.close()
    print 'Connecting to Word...'
    f = EditorProcess(fn)
    print 'Attached to %s %s' % (`f.wordapp`, f.wordapp.Version)
    print ('%s is open...' % fn),
    if f.isAlive():
        print 'yes'
        print 'Test Passed.'
    else:
        print 'no'
        print 'Test Failed.'
    
if __name__ == '__main__':
    test()
