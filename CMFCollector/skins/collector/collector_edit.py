## Script (Python) "collector_edit.py"
##parameters=title, description, email, abbrev, supporters, topics, classifications, importances, severities, versions, other_versions_spiel
##title=Configure Collector
 
changed = context.edit(title=title,
                       description=description,
                       abbrev=abbrev,
                       email=email,
                       supporters=supporters,
                       topics=topics,
                       classifications=classifications,
                       importances=importances,
                       severities=severities,
                       versions=versions,
                       other_versions_spiel=other_versions_spiel)

qst='?portal_status_message=Configuration+%s.' % ((changed and "changed")
                                                  or "unchanged")
 
context.REQUEST.RESPONSE.redirect(context.absolute_url() + qst )

