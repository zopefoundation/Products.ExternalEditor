## Script (Python) "collector_add_issue.py"
##parameters=submitter, title, security_related, topic, importance, classification, severity, description, reported_version, other_version_info
##title=Submit a Request

REQUEST = context.REQUEST

id = context.add_issue(submitter=submitter,
                       title=title,
                       description=description,
                       security_related=security_related,
                       topic=topic,
                       importance=importance,
                       classification=classification,
                       severity=severity,
                       reported_version=reported_version,
                       other_version_info=other_version_info,
                       assignees=REQUEST.get('assignees'),
                       file=REQUEST.get('file'),
                       fileid=REQUEST.get('fileid', ''),
                       filetype=REQUEST.get('filetype', 'file'))

context.REQUEST.RESPONSE.redirect("%s/%s" % (context.absolute_url(), id))

