##parameters=request=None
##title=Pre-process form variables and return a batch of catalog query results.
##
if request is None:
    request = container.REQUEST

query = request.form.copy()
for key, value in query.items():
    if not value:
        del query[key]

if query.get('creation_from_date') and query.get('creation_to_date'):
    query['CreationDate'] = {
        'query': [query['creation_from_date'],
                  query['creation_to_date']],
        'range': 'min:max'}

if query.get('Subject'):
    q = filter(None, query['Subject'])
    if not q:
        del query['Subject']
    else:
        query['Subject'] = q

results = context.portal_catalog(query)

total = len(results)
b_start = int(request.get('b_start', 1))
b_count = int(request.get('b_count', 20))
b_end = b_start + b_count - 1

from ZTUtils import make_query
url = request['URL']

if b_end >= total:
    b_end = total
if b_start > 1:
    n = b_start - b_count
    if n < 1:
        n = 1
    prev_url = '%s?%s' % (url, make_query(request.form, b_start=n))
else:
    prev_url = ''
if b_end < total:
    n = b_end + 1
    next_url = '%s?%s' % (url, make_query(request.form, b_start=n))
else:
    next_url = ''

batch = []
for item in results[b_start - 1:b_end]:
    batch.append((item.getPath(), item.getObject()))

return {
    'batch': batch,
    'total': total,
    'b_start': b_start,
    'b_end': b_end,
    'prev_url': prev_url,
    'next_url': next_url,
    }
