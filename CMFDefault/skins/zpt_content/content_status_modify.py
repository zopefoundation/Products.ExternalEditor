## Script (Python) "content_status_modify"
##parameters=workflow_action, comment=''
##title=Modify the status of a content object
 
context.portal_workflow.doActionFor(
    context,
    workflow_action,
    comment=comment)

if workflow_action == 'reject':
    redirect_url = context.portal_url() + '/search?review_state=pending'
else:
    redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=Status+changed.'
                                  )

context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )

