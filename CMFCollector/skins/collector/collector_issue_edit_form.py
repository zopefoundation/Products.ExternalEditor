## Script (Python) "collector_issue_edit_form.py"
##parameters=
##title=Redirect to issue contents with edit parameter
 
context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?do_edit=1')

