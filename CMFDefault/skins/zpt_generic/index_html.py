##parameters=b_start=0
##
from ZTUtils import Batch

options = {}

options['has_local'] = 'local_pt' in context.objectIds()

key, reverse = context.getDefaultSorting()
items = context.listFolderContents()
items = sequence.sort( items, ((key, 'cmp', reverse and 'desc' or 'asc'),) )
batch_obj = Batch(items, 25, b_start, orphan=0)
listItemInfos = context.getBatchItemInfos(batch_obj)
target = context.getActionInfo('object/view')['url']
navigation = context.getBatchNavigation(batch_obj, target)
options['batch'] = { 'listItemInfos': listItemInfos,
                     'navigation': navigation }

return context.index_html_template(**options)
