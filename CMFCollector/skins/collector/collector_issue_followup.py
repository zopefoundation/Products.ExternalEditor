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

if context.status() in ['Resolved', 'Rejected', 'Deferred']:
    collector = context.aq_parent
    destination = collector.absolute_url()
    if len(collector) > int(context.id):
        destination = destination + "?b_start:int=%s" % int(context.id)
else:
    destination = context.absolute_url()

context.REQUEST.RESPONSE.redirect(destination)
