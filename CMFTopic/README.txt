Updating CMF Topic in a CMF Site

  Since default settings may change from time to time in CMF Topic,
  you may need to update your Topic types tool (and other) settings.
  This is done similarly to installing by adding an External Method
  to your CMF Site instance with the following configuration::

    **id** -- 'update_topic'
    **title** -- *Update Topic*
    **module name** -- 'CMFTopic.Update'
    **function name** -- 'update'

  Go to the management screen for the newly added external method and
  click the 'Try it' tab.  The update function will execute and give
  information about the steps it took to register and update CMF Topic 
  site information.

  *Note: This update script should **only** change values that are
  still at their default, such as changing an action from 'topic_edit' 
  to 'topic_edit_form'.  If you changed that action to 'mytopic_edit', 
  the script should pass that by and not change your settings.*
