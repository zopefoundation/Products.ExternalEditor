## Script (Python) "search_results_control"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=b_start=0, **kw
##title=
##
from Products.PythonScripts.standard import thousands_commas
from ZTUtils import Batch
from Products.CMFCore.utils import getToolByName
ctool = getToolByName(script, 'portal_catalog')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
epoch = DateTime('1970/01/01 00:00:01 GMT')


control = {}

target = '%s/search' % portal_url
for k, v in kw.items():
    if k in ('review_state', 'Title', 'Subject', 'Description', 'portal_type',
             'listCreators'):
        if same_type(v, []):
            v = filter(None, v)
        if not v:
            del kw[k]
    elif k in ('created',):
        if v['query'] == epoch and v['range'] == 'min':
            del kw[k]
        else:
            # work around problems with DateTime in records
            kw[k] = v.copy()
    elif k in ('go', 'go.x', 'go.y'):
            del kw[k]
items = ctool.searchResults(kw)
batch_obj = Batch(items, 25, b_start, orphan=1)
length = batch_obj.sequence_length
summary = { 'length': length and thousands_commas(length) or '',
            'type': (length == 1) and 'item' or 'items',
            'match': kw.get('SearchableText') }
navigation = context.getBatchNavigation(batch_obj, target, **kw)
control['batch'] = { 'summary': summary,
                     'listItemBrains': batch_obj,
                     'navigation': navigation }

return control
