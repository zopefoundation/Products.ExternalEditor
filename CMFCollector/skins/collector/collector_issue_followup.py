## Script (Python) "collector_issue_followup.py"
##parameters=comment, action
##title=Submit a new comment.

context.portal_workflow.doActionFor(context,
                                    action,
                                    comment=comment)

attachments = context.REQUEST.get('attachments', [])
id = context.do_action(action, comment, attachments)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
