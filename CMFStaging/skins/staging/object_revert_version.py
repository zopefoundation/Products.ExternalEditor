##parameters=version_id, REQUEST=None
##title=Revert to a specific revision of an object

if context.portal_lock.locked(context):
    context.portal_lock.unlock(context)

context.portal_versions.revertToVersion(context, version_id)

if REQUEST is not None:
    msg = 'Reverted+to+revision+%s.' % version_id
    view = 'object_version_control_form'
    REQUEST.RESPONSE.redirect(
        '%s/%s?portal_status_message=%s' % (
        context.absolute_url(), view, msg))
