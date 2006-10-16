; Zope External Editor Inno Setup Script

[Setup]
DisableStartupPrompt=yes
AppName=Zope External Editor Helper Application
AppVerName=Zope External Editor 0.9.3
AppPublisher=Casey Duncan, Zope Corporation (maintained by Chris McDonough)
AppPublisherURL=http://plope.com/software/ExternalEditor
AppVersion=0.9.3
AppSupportURL=http://plope.com/software/ExternalEditor
AppUpdatesURL=http://plope.com/software/ExternalEditor
DefaultDirName={pf}\ZopeExternalEditor
DefaultGroupName=Zope External Editor
AllowNoIcons=yes
LicenseFile=..\LICENSE.txt
ChangesAssociations=yes
OutputBaseFilename=zopeedit-win32-0.9.3

[Registry]
; Register file type for use by helper app
Root: HKCR; SubKey: "Zope.ExternalEditor"; ValueType: string; ValueData: "Zope External Editor"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "Zope.ExternalEditor"; ValueType: binary; ValueName: "EditFlags"; ValueData: "00 00 01 00"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "Zope.ExternalEditor\shell"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "Zope.ExternalEditor\shell\open"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "Zope.ExternalEditor\shell\open\command"; ValueType: string; ValueData: """{app}\zopeedit.exe"" ""%1"""; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: ".zope"; ValueType: string; ValueData: "Zope.ExternalEditor"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: ".zope"; ValueType: string; ValueName: "PerceivedType"; ValueData: "Zope"; Flags: uninsdeletevalue
Root: HKCR; SubKey: ".zope"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-zope-edit"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "MIME\Database\Content Type\application/x-zope-edit"; ValueType: string; ValueName: "Extension"; ValueData: ".zope"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "MIME\Database\Content Type\application/x-zope-edit"; Flags: uninsdeletekeyifempty

[Files]
Source: "..\dist\*.*"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "ZopeEdit.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "ZopeExtEditDummyOCX.ocx"; DestDir: "{app}"; Flags: restartreplace regserver
Source: "..\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGES.txt"; DestDir: "{app}"; Flags: ignoreversion

