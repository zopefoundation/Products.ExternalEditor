## Script (Python) "collector_issue_followup.py"
##parameters=comment, action="comment"
##title=Submit a new comment.

REQUEST = context.REQUEST

context.do_action(action,
                  comment,
                  assignees=REQUEST.get('assignees', []),
                  file=REQUEST.get('file'),
                  fileid=REQUEST.get('fileid', ''),
                  filetype=(REQUEST.get('filetype', 'file')))

if context.status() in ['Resolved', 'Rejected', 'Deferred']:
    destination = context.aq_parent.absolute_url()
else:
    destination = context.absolute_url()

context.REQUEST.RESPONSE.redirect(destination)
