## Script (Python) "collector_issue_edit.py"
##parameters=
##title=Submit a Request

REQUEST = context.REQUEST

import pdb; pdb.set_trace()

id = context.edit(comment=REQUEST.get('comment'),
                  status=REQUEST.get('status'),
                  submitter_name=REQUEST.get('submitter_name'),
                  title=REQUEST.get('title'),
                  description=REQUEST.get('description'),
                  security_related=REQUEST.get('security_related'),
                  topic=REQUEST.get('topic'),
                  importance=REQUEST.get('importance'),
                  classification=REQUEST.get('classification'),
                  severity=REQUEST.get('severity'),
                  reported_version=REQUEST.get('reported_version'),
                  other_version_info=REQUEST.get('other_version_info'))

context.REQUEST.RESPONSE.redirect("%s/collector_issue_contents"
                                  % context.absolute_url())

