## Script (Python) "collector_issue_followup.py"
##parameters=comment, action
##title=Submit a new comment.

REQUEST = context.REQUEST

context.do_action(action,
                  comment,
                  assignees=REQUEST.get('assignees', []),
                  file=REQUEST.get('file'),
                  fileid=REQUEST.get('fileid', ''),
                  filetype=(REQUEST.get('filetype', 'file')))

context.REQUEST.RESPONSE.redirect(context.absolute_url())
