##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""External Editor Dreamweaver Plugin

Contributed by Manuel Aristarann (relicensed by permission)
$Id$
"""

from time import sleep
import win32process
import win32con
import win32event
import win32api
import os
from win32com.client import GetObject


class EditorProcess:
    def __init__(self, file):
        """Launch editor process"""
        # let's see if DW's already running
        # kind of a hack, but...
        WMI = GetObject('winmgmts:')
        dwprocesses = WMI.ExecQuery(
            'select * from Win32_Process where Name="Dreamweaver.exe"')
	dwPath = getDWPathFromRegistry()
        if dwPath is None:
	    raise RuntimeError('Cannot find dreamweaver.exe')
        processinfo = win32process.CreateProcess(
                None,
                '%s %s' % (dwPath, file),
                None,   
                None,
                1,
                win32process.CREATE_NEW_CONSOLE,
                None,
                None,
                win32process.STARTUPINFO())
        if len(dwprocesses):
	    # DW is already running
            self.pid = dwprocesses[0].Properties_('ProcessId').Value
            self.hProcess = win32api.OpenProcess(
	        win32con.PROCESS_ALL_ACCESS, 0, self.pid)
	else:
            self.hProcess, nil, self.pid, nil = processinfo
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        win32event.WaitForSingleObject(self.hProcess, int(timeout * 1000.0))
                    
    def isAlive(self):
        """Returns true if the editor process is still alive"""
        return win32process.GetExitCodeProcess(self.hProcess) == 259


# must get Dreamweaver's path from registry
from win32api import RegOpenKey, RegQueryValue, RegCloseKey
from win32con import HKEY_LOCAL_MACHINE

def getDWPathFromRegistry():
    try:
        hkey = RegOpenKey(HKEY_LOCAL_MACHINE,
                   r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths')
        value = RegQueryValue(hkey, 'Dreamweaver.exe')
    except:
        value = None
    RegCloseKey(hkey)
    return value


def test():
    print 'Spawining DW Process...'
    f = EditorProcess('C:\\test.html')
    if f.isAlive():
        print 'yes'
        print 'Test Passed.'
    else:
        print 'no'
        print 'Test Failed.'
    
if __name__ == '__main__':
    test()

