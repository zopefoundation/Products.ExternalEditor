##parameters=type, id=None, title='', return_object=0, lock_object=1
##title=Adds an object to a BTreeFolder and makes a link in the workspace
# Also generates the ID if necessary, assuming that dest is a BTreeFolder2.

dest = context.portal_organization.getTypeContainer(type)

if id is None:
    prefix = '%s-%s-' % (container.ZopeTime().strftime('%Y%m%d%H%M'),
                         type.replace(' ', ''))
    id = dest.generateId(prefix, rand_ceiling=9999)

if not dest.checkIdAvailable(id):
    return dest.error_id_in_use()

REQUEST = context.REQUEST
RESPONSE = context.REQUEST['RESPONSE']
dest.invokeFactory(type, id, title=title, RESPONSE=RESPONSE)

ob = dest[id]
workspace = REQUEST.get('workspace')
if workspace:
    ws = context.restrictedTraverse(workspace)
    ws.addReference(ob)
if lock_object: context.portal_lock.lock(ob) # Lock it on creation

# Note that invokeFactory() causes a redirection.
if return_object:
    return ob
else:
    return ''
