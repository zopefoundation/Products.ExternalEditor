## Script (Python) "content_status_modify"
##parameters=workflow_action, comment=''
##title=Modify the status of a content object
 
context.portal_workflow.doActionFor(
    context,
    workflow_action,
    comment=comment)

context.REQUEST[ 'RESPONSE' ].redirect( '%s/view?%s'
                   % ( context.absolute_url()
                     , 'portal_status_message=Status+changed.'
                     ) )

