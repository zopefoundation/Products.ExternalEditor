## Script (Python) "getBatchNavigation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch_obj, target, type_singular='item', type_plural='items', previous_text='Previous', next_text='Next', **kw
##title=
##
from ZTUtils import make_query
if kw.has_key('b_start'):
    del kw['b_start']
if kw.has_key('portal_status_message'):
    del kw['portal_status_message']

navigation = {}

items = []
for batch in (batch_obj.previous, batch_obj.next):
    length = batch and batch.length or 0
    if length:
        batch_start = batch.first
        if batch_start:
            kw['b_start'] = batch_start
        query = kw and ( '?%s' % make_query(kw) ) or ''
        url = '%s%s' % (target, query)
    items.append( {'length': length > 1 and length or '',
                   'type': length == 1 and type_singular or type_plural,
                   'url': length and url or ''} )
navigation['previous'] = items[0]
navigation['previous']['text'] = previous_text
navigation['next'] = items[1]
navigation['next']['text'] = next_text

return navigation
