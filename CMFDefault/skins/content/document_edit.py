## Script (Python) "document_edit"
##parameters=text_format, text, file='', SafetyBelt='', change_and_view=''
##title=Edit a document
try:
    from Products.CMFDefault.utils import scrubHTML
    text = scrubHTML( text ) # Strip Javascript, etc.
    context.edit( text_format
                , text
                , file
                , safety_belt=SafetyBelt
                )
    qst='portal_status_message=Document+changed.'

    if change_and_view:
        target_action = context.getTypeInfo().getActionById( 'view' )
    else:
        target_action = context.getTypeInfo().getActionById( 'edit' )

    context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
except Exception, msg:
    target_action = context.getTypeInfo().getActionById( 'edit' )
    context.REQUEST.RESPONSE.redirect(
        '%s/%s?portal_status_message=%s' % ( context.absolute_url()
                                           , target_action
                                           , msg
                                           ) )
