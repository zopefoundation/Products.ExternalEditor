## Script (Python) "search_collector.py"
##title=Build Collector Search

query = {}
query['sort_on'] = 'id'
query['Type'] = "Collector Issue"
query['path'] = context.absolute_url(1)

reqget = context.REQUEST.get
subj_items = []

def supplement_query(field, index_name=None, reqget=reqget, query=query):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        query[index_name] = val
def supplement_subject_one(field, index_name=None, reqget=reqget, items=subj_items):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        items.append('%s:%s' % (index_name, val))
def supplement_subject_many(field, index_name=None, reqget=reqget, items=subj_items):
    if not index_name: index_name = field
    vals = reqget(field, [])
    for i in vals:
        items.append('%s:%s' % (index_name, i))

supplement_query("SearchableText")
supplement_query("Creator")
supplement_query("status", "review_state")
supplement_subject_many("classifications", "classification")
supplement_subject_many("severities", "severity")
supplement_subject_many("supporters", "assigned_to")
supplement_subject_one("resolution")
supplement_subject_one("security_related")
supplement_subject_one("reported_version")
if subj_items:
    query["Subject"] = subj_items

return context.portal_catalog(REQUEST=query)

# Use "sort_on='index_name'" to sort - default, id
