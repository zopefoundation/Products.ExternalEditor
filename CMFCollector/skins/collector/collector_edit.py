## Script (Python) "collector_edit.py"
##parameters=title, description, email, abbrev, managers, supporters, dispatching, topics, classifications, importances, version_info_spiel
##title=Configure Collector
 
from Products.PythonScripts.standard import url_quote_plus

changes = context.edit(title=title,
                       description=description,
                       abbrev=abbrev,
                       email=email,
                       managers=managers,
                       supporters=supporters,
                       dispatching=dispatching,
                       topics=topics,
                       classifications=classifications,
                       importances=importances,
                       version_info_spiel=version_info_spiel)

if not changes:
    changes = "No configuration changes"
else:
    changes = "Changed: " + changes

if context.REQUEST.get('recatalog', None):
    context.reinstate_catalog()
    changes = changes + ", Reinstated catalog"

msg = '?portal_status_message=%s.' % url_quote_plus(changes)
 
context.REQUEST.RESPONSE.redirect("%s/%s%s"
                                  % (context.absolute_url(),
                                     "collector_edit_form",
                                     msg))

