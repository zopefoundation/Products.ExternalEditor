## Script (Python) "collector_add_issue.py"
##parameters=title, security_related, submitter_email, topic, importance, classification, description, version_info
##title=Submit a Request

REQGET = context.REQUEST.get

id = context.add_issue(title=title,
                       security_related=security_related,
                       submitter_name=REQGET('submitter_name'),
                       submitter_email=submitter_email,
                       description=description,
                       topic=topic,
                       classification=classification,
                       importance=importance,
                       version_info=version_info,
                       assignees=REQGET('assignees', []),
                       file=REQGET('file'),
                       fileid=REQGET('fileid', ''),
                       filetype=REQGET('filetype', 'file'))

context.REQUEST.RESPONSE.redirect("%s/%s" % (context.absolute_url(), id))

