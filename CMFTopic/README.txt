Installing CMF Topic into a CMF Site

 Since the CMF allows site by site configuration, just having CMF
 Topic installed into your Zope does not mean that any CMF Site
 instance will know what to do with it.  To get CMF Topic installed
 and registered, you need to go to the root of the CMF Site (aka
 *Portal* instance) that you want CMF Topic to be registered in and add an 
 External Method with the following configuration:

   **id** -- 'install_topic'
   **title** -- *Install Topic*
   **module name** -- 'CMFTopic.Install'
   **function name** -- 'install'

 Then go to the management screen for the newly added external method
 and click the 'Try it' tab.  The install function will execute and give
 information about the steps it took to register and install the CMF Topic
 into the CMF Site instance.
