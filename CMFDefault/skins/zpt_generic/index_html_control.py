## Script (Python) "index_html_control"
##parameters=b_start=0
##title=
##
from ZTUtils import Batch

control = {}

key, reverse = context.getDefaultSorting()
items = context.listFolderContents()
items = sequence.sort( items, ((key, 'cmp', reverse and 'desc' or 'asc'),) )
batch_obj = Batch(items, 25, b_start, orphan=0)
listItemInfos = context.getBatchItemInfos(batch_obj)
target = context.getActionInfo('object/view')['url']
navigation = context.getBatchNavigation(batch_obj, target)
control['batch'] = { 'listItemInfos': listItemInfos,
                     'navigation': navigation }

return control
