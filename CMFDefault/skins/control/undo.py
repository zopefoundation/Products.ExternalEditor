## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info
try:
    context.portal_undo.undo(context, transaction_info)
except:
    return context.REQUEST.RESPONSE.redirect(
        'folder_contents?portal_status_message=Transaction(s)+could+not+be+undone.' )
    
return context.REQUEST.RESPONSE.redirect(
    'folder_contents?portal_status_message=Transaction(s)+undone' )
