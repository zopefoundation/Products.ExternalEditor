## Script (Python) "search_collector.py"
##title=Build Collector Search

query = {}
query['Type'] = "Collector Issue"
query['path'] = context.absolute_url(1)

reqget = context.REQUEST.get
subj_items = []

def supplement_query(field, reqget=reqget, query=query):
    val = reqget(field, None)
    if val:
        query[field] = val
def supplement_subject_one(field, reqget=reqget, items=subj_items):
    val = reqget(field, None)
    if val:
        items.append('%s:%s' % (field, val))
def supplement_subject_many(field, reqget=reqget, items=subj_items):
    vals = reqget(field, [])
    for i in vals:
        items.append('%s:%s' % (field, i))

supplement_query("SearchableText")
supplement_query("Creator")
supplement_subject_many("classifications")
supplement_subject_many("severities")
supplement_subject_one("resolution")
supplement_subject_one("security_related")
supplement_subject_one("reported_version")
supplement_subject_one("security_related")
supplement_subject_one("reported_version")
if query:
    query["Subject"] = subj_items

return context.portal_catalog(REQUEST=query)
