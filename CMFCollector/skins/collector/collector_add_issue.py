## Script (Python) "collector_add_issue.py"
##parameters=id=None, title='', description='', submitter_id=None, submitter_name=None, submitter_email='', supporters=(), kibitzers=(), security_related=0, topic=None, importance=None, classification=None, version_info=None, invisible=0, file=None, fileid=None, filetype=None
##title=Submit a Request

from Products.PythonScripts.standard import url_quote_plus

REQGET = context.REQUEST.get

id, issue = context.add_issue( id, title, description )

#  The following methods return changes, which we don't care about, as
#  this is initial creation.
issue.setSubmitter( submitter_id, submitter_name, submitter_email or None )
issue.setSupporters( supporters )
issue.setKibitzers( kibitzers )

issue.setSecurityRelated( security_related )
issue.setTopic( topic )
issue.setClassification( classification )
issue.setImportance( importance )
issue.setVersionInfo( version_info )

#   Set initial transcript text, workflow state.
err = issue.do_action( 'request', description, file, fileid, filetype )

dest = "%s/%s" % (context.absolute_url(), id)

if err:
    dest += '?portal_status_message=' + url_quote_plus(err)

context.REQUEST.RESPONSE.redirect(dest)

