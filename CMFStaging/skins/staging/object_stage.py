##parameters=stage_names, comments, REQUEST=None
##title=Stage an object

context.portal_staging.updateStages2(context, stage_names, comments)
if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url() + "/view")
