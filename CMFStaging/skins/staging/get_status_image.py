##parameters=stage='dev'
##title=Get image for content's locked/synced status per specified stage.

if stage == 'dev':
    lt = getattr(context, 'portal_lock', None)
    if lt is not None:
        locker = lt.locked(context) and lt.locker(context)
    else:
        locker = None

    if locker:
        from AccessControl import getSecurityManager
        username = getSecurityManager().getUser().getUserName()

        if locker == username:
            return getattr(context, "status_locked.gif")
        else:
            return getattr(context, "status_locked_out.gif")

st = getattr(context, 'portal_staging', None)
if st is None or not st.isStageable(context):
    return None

versions = st.getVersionIds(context)
if not versions[stage]:
    return None

if not versions['prod'] or versions[stage] != versions['prod']:
    return getattr(context, "status_unsynced.gif")

return getattr(context, "status_synced.gif")
