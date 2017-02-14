Changelog
=========


2.0.2 (2017-02-14)
------------------

- Fixed reflective XSS in findResult.
  This applies PloneHotfix20170117.  [maurits]


2.0.1 (2016-09-08)
------------------

- Quote variable in manage_tabs to avoid XSS.
  From Products.PloneHotfix20160830.  [maurits]


2.0.0 (2015-09-09)
------------------

- Moved code to https://github.com/zopefoundation/Products.ExternalEditor

- Update dtml to Zope trunk.


1.1.0 (2010-12-01)
------------------

- Added support for unaware mimetype browser - we now add the .zem extension no
  matter what the user-agent

- Modified the cache's parameters - special case for MSIE

- Corrected and added tests

- Moved the sources of the client to another package : collective.zopeedit


1.0 (2010-07-01)
----------------

- Update manage_main, manage_tabs, and findResult monkey patches to include
  fixes from Zope 2.12.


1.0a2 (2009-11-13)
------------------

- Removed imports from Globals.

- Purged old Zope 2 Interface interfaces for Zope 2.12 compatibility.


1.0a1 (2008-03-05)
------------------

- Updated package metadata to be usable as a package.


01/03/2007 - 0.9.3
------------------

- Fixed issue with 'manage_FTPget' overriding the 'Content-Type'
  header.

- Only run ExpandEnvironmentStrings on win32 systems.


9/14/2006 - 0.9.2
-----------------

- Added 'skip_data' option to make External Editor send out only
  the metadata part and skip appending data to the 'body'.

- Add a simple callback registry that can be used to add extra
  metadata headers or set special response headers when a file is
  edited through External Editor.

- Use rfc822.Message for parsing the metadata of the file being
  edited.

- Don't emit a warning about deprecated 'methods' in Zope >= 2.10.

- Fixed acquisition issue in manage_main.dtml to sync up with the
  same fix applied to Zope.


6/23/2005 - 0.9.1
-----------------

- Older pyc files for plugins were included in the 0.9 release.
  This version has the most up to date plugins.


6/20/2005 - 0.9
---------------

- When using the Excel plugin, errors were seen by users like
  "TypeError: This object does not support enumeration".  We now
  make the user deal with these.

- When using the Excel plugin, errors were intermittently raised to the
  user in the form "Fatal error: <unknown>.Path" and the user could
  subsequently not save the document back to Zope because the
  external editor process had quit.

- Changes to documents intermittently may not have been saved back to Zope
  when using any plugin that involved COM (Word, Excel, Powerpoint, etc).

- If Word was exited before a user actively saved, if there were
  outstanding changes in the document being edited, those changes
  would not be saved to the server despite the user answering
  "yes" to the "do you want to save before you exit" dialog
  presented by Word.

- The "title" attribute of the object being externally edited is
  now available within the set of headers returned by EE to the
  zopeedit client.

- Detecting whether the client has External Editor installed from
  within IE using JavaScript or VBScript is now possible, assuming
  that the client software is installed via the InnoSetup
  installer.  See "win32/ocx.txt" for more info.

- External Editor now compatible with objects that return a
  "filestream iterator" in Zope 2.7.1+. (if upgrading: this fix
  does not require an update to EE client, just the EE Zope
  product).

- Properly escape hyphens in man page. Thanks to Federico Sevilla III.

- Check if the editor was launched before locking the file in Zope. This
  prevents errors if the editor is closed before the lock request
  completes.

- Do not ask the user what editor to use on Posix platforms. Instead just
  tell the user to edit the config file. The askstring()
  function does not work with a hidden root Tk window in Python 2.3.4.
  Thanks to Christopher Mann.


7/13/04 - 0.8
-------------

- Add external editor icon to ZMI breadcrumbs for editable objects.

- Compiled windows helper app binary using Python 2.3.4, Pythonwin build
  163 and py2exe 0.5.

- Add Dreamweaver plugin contributed by Manuel Aristarann. Thanks also
  to Anton Stonor.

- Add ZMI support for Zope 2.7's ordered folder objects.

- Fix bug detecting basic auth info from older versions of CookieCrumber.
  Thanks to David D. Smith and Federico Sevilla III.

- Workaround IE browser error when running over SSL. Thanks to
  Marc-Aurele Darche.

- Add ".zem" file extension support for MacOS X (especially Mac IE),
  to ease helper app integration where MIME support is lacking. Thanks
  to Zac Bir.

- Added "long_file_name" and "file_name_separator" config options.

- Fixed bug which happened under Win32 when editing an Excel file
  using the Excel plugin where the symptom was a "Call was
  rejected by callee" COM error. Thanks to Chris McDonough.


4/23/04 - 0.7.2
---------------

- Change default configuration to use .txt extension for text/plain only.
  Add extensions for css and javascript files.

- Fixed packaging bug in Windows binary which disabled several plugins.
  This fixes "Editor did not launch properly" errors for MSOffice
  among others.

- Fixed a bug where very short editing sessions where no changes were
  made could make EE think the editor never launched. Thanks to Maik Ihde.

11/7/03 - 0.7.1
---------------

- Fix encoding bug in windows binary. Thanks to Chris McDonough.

- Added tip for configuring IE to save files over SSL. Thanks to
  Jonah Bossewitch.


4/1/03 - 0.7
------------

- Added working distutils setup for Unix.

- You can now specify from the server that the helper app should
  borrow a lock by passing borrow_lock=1 via the request, thus
  suppressing the dialog box which appears by default. Thanks
  to Shane Hathaway.

- Improved open file check in Word and Powerpoint plugins
  thanks to Yura Petrov.

- Added plugins for Microsoft Word, Excel and Powerpoint.

- Added the man page from the Debian distro. Thanks go out to
  Federico Sevilla III and Andreas Tille


11/02/02 - 0.6
--------------

- Built Windows helper app using Python 2.2.2 and PythonWin 148.

- The `externalEdit_` object now accepts a path argument to the object to
  edit, allowing URLs like: `http://zope/externalEdit_?path=/some/object.`
  This allows external editor to play better with applications making use
  of traversal magic of their own. Thanks to Tres Seaver.

- Fixed NameError bug in unlock retry code. Thanks to Federico Sevilla III.

- Added a workaround for non-compliant SSL servers. The software now
  silently ignores "EOF occurred in violation of protocol" errors coming
  from httplib. Thanks to Christopher Deckard.

- Removed stderr writes to cure "Invalid File Descriptor" errors on
  Windows. Thanks to Martijn Peters.

- Added Photoshop plugin (win32)

- Added HomeSite plugin (win32)

- Added win32 editor plugin support for the helper application.


8/19/02 - 0.5
-------------

- Added patch for Zope find template so that you can use external editor
  directly from find results in the ZMI. Thanks to Jim Washington.

- Factored out external editor link generator. Product now registers
  a global method `externalEditLink_` which can be called to generate
  the external editor icon link for any object.

- External editing is now governed by the "Use external editor" permission
  to allow non-managers to use it. Users must also have the permissions to
  edit/modify the objects they edit, plus do WebDAV locking if desired.
  Thanks to Reineke and others.

- Unix editor command line parsing is much more robust now and properly
  handles quoted arguments. You can also specify the "$1" placeholder in the
  editor command to denote where the content file name is inserted. If
  omitted it is appended to the end of the command line. "%1" continues to
  work similarly for Windows. Thanks to Marc St-Jean.

- Fixed bug editing large (chunked) files and images. External editor now
  streams their data properly to the client. Thanks to all the users who
  reported various symptoms of this bug.

- Fixed bug editing objects inside a Squishdot site. Thanks to Kevin Salt.

- Added the capability to borrow exising DAV locks. This allows external
  editor to play well with other systems using locks, such as CMFStaging. A
  new configuration flag, always_borrow_locks can be set to suppress the
  borrow lock warning dialog when editing.

- Fixed auth bug when product was used with mysqlUserFolder. Thanks to
  ViNiL.


6/30/02 - 0.4.2
---------------

- Added SSL support to Windows binary package. Thanks to Federico
  Sevilla III


6/29/02 - 0.4.1
---------------

- Fixed dangling dav lock bug on fatal errors. Thanks to Marc St-Jean.

- Fixed content_type bug, now checks if it is callable. Thanks to Arnaud
  Bienvenu.

- Fixed bug with editing binary data on Windows. Thanks to Eric Kamm.

- Fixed bug setting the editor on Posix platforms.


6/24/02 - 0.4
-------------

- Added --version command line argument

- Made manage_FTPget the default source for the editable content, instead
  of document_src which was broken for CMF Wiki Pages.

- Fixed Windows "body_file" bug.

- Added binary build support for Windows using py2exe and Inno setup.

- Fixed Windows config file locator. It now looks in the program directory
  and then the user's home directory (if specified)

- Fixed bug in Windows registry editor lookup.


6/16/02 - 0.3
-------------

- Improved behavior when saving after lock attempts fail.

- Now works on Windows (applause) using Pythonwin. Much overall
  refactoring to abstract process control. Thanks to Oliver Deckmyn,
  Gabriel Genellina and Arno Gross for testing, patches and suggestions.

- Added "temp_dir" configuration option for specifying a different
  temp file directory then the OS default. Also further improved
  temp file name generation.

- Added support for domain specific configuration options.

- Fixed trailing newline bug in encoded auth data coming from
  CookieCrumbler. Thanks to Harald Koschinski.

- You can now pass command line arguments to the editor in the config file,
  or wrap the editor in an xterm without using a shell script.

- Rewrote "Editor did not launch" error message so it makes more sense.

- Fixed https detection bug. External editor is now tested and working with
  https. Many thanks to Hans-Dieter Stich and Martin Groenemeyer for their
  assistance and ideas.

- Made it possible to edit objects that are methods of ZClasses. Thanks to
  Jim Washington

- Refactored link generation code in manage_main so that it uses
  the parent's absolute_url rather than URL1. Thanks to
  Jim Washington

- Removed implicit save in Configuration class destructor

- Added caching headers to prevent client-side caching of edit data.
  Thanks to Gabriel Genellina for pointing this out.

- Added improved support for editing CMF documents

- Eliminated spurious "Editor did not launch" errors on short sessions
  or when other errors occurred.

5/16/02 - 0.2
-------------

- Fixed product uninstallation bug

5/15/02 - 0.1
-------------

- Initial release
