## Script (Python) "collector_issue_followup.py"
##parameters=comment, action
##title=Submit a new comment.

context.do_action(action,
                  comment,
                  attachments=context.REQUEST.get('attachments', []),
                  assignees=context.REQUEST.get('assignees', []))

context.REQUEST.RESPONSE.redirect(context.absolute_url())
