## Script (Python) "collector_search.py"
##title=Build Collector Search

query = {}
query['sort_on'] = 'created'
query['Type'] = "Collector Issue"
query['path'] = "/".join(context.getPhysicalPath())

reqget = context.REQUEST.get
subj_items = []

def supplement_query(field, index_name=None, reqget=reqget, query=query):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        query[index_name] = val
def supplement_subject_one(field, index_name=None,
                           reqget=reqget, items=subj_items):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        items.append('%s:%s' % (index_name, val))
def supplement_subject_many(field, index_name=None,
                            reqget=reqget, items=subj_items):
    if not index_name: index_name = field
    vals = reqget(field, [])
    for i in vals:
        items.append('%s:%s' % (index_name, i))

supplement_query("SearchableText")
supplement_query("Creator")
supplement_subject_many("classifications", "classification")
supplement_subject_many("severities", "severity")
supplement_subject_many("supporters", "assigned_to")
supplement_subject_one("resolution")
supplement_subject_one("reported_version")

sr = reqget("security_related", [])

if sr:
    if 'Yes' in sr and 'No' in sr:
        pass
    elif 'Yes' in sr:
        subj_items.append('security_related:1')
    else:
        subj_items.append('security_related:0')

if subj_items:
    query["Subject"] = subj_items

rs = []
for i in reqget("status", []):
    rs.append(i)
    # Include confidential alternatives to selected states.
    if i in ['Pending', 'Accepted']:
        rs.append("%s_confidential" % i)
if rs:
    query['review_state'] = rs

return context.portal_catalog(REQUEST=query)
