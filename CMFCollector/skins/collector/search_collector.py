## Script (Python) "search_collector.py"
##parameters=path, Type, SearchableText=None, Creator=None, classifications=None, severities=None, resolution=None, security_related=None, reported_version=None
##title=Build Collector Search
subj_items = []
if classifications:
    for i in classifications:
        subj_items.append('classification:%s' % (i))
if severities:
    for i in severities:
        subj_items.append('severity:%s' % (i))
if resolution:
    subj_items.append('resolution:%s' % (resolution))
if security_related:
    subj_items.append('security_related:' % (security_related))
if reported_version:
    subj_items.append('reported_version:' % (reported_version))
q = {}
q['path'] = path
q['Type'] = Type
if Creator:
    q['Creator'] = Creator
if subj_items:
    q['Subject'] = subj_items
return context.portal_catalog(REQUEST=q)
