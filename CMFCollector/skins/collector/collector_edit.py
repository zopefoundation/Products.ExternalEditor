## Script (Python) "collector_edit.py"
##parameters=title, description, email, abbrev, supporters, topics, classifications, importances, severities, versions, other_versions_spiel
##title=Configure Collector
 
from Products.PythonScripts.standard import url_quote_plus

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

if changed:
    changes = "Configuration changed"
else:
    changes = "No configuration changes"

if context.REQUEST.get('recatalog', None):
    context.reinstate_catalog()
    changes = changes + ", reindexed"

msg = '?portal_status_message=%s.' % url_quote_plus(changes)
 
context.REQUEST.RESPONSE.redirect(context.absolute_url() + msg)

