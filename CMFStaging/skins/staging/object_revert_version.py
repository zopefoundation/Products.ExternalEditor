##parameters=version_id, REQUEST=None
##title=Revert to a specific revision of an object

if context.LockTool.locked(context):
    context.LockTool.unlock(context)

context.StagingTool.revertToVersion(context, version_id)

if REQUEST is not None:
    msg = 'Reverted to revision %s.' % version_id
    view = 'object_version_control_form'
    REQUEST.RESPONSE.redirect(
        '%s/%s?portal_status_message=%s' % (
        context.absolute_url(), view, msg))
