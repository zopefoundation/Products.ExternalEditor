## Script (Python) "metadata_edit"
##title=Update Content Metadata
##parameters=title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None

def tuplify( value ):

    if not same_type( value, () ):
        value = tuple( value )

    temp = filter( None, value )
    return tuple( temp )

if title is None:
    title = context.Title()

if subject is None:
    subject = context.Subject()
else:
    subject = tuplify( subject )

if description is None:
    description = context.Description()

if contributors is None:
    contributors = context.Contributors()
else:
    contributors = tuplify( contributors )

if effective_date is None:
    effective_date = context.EffectiveDate()

if expiration_date is None:
    expiration_date = context.expires()

if format is None:
    format = context.Format()

if language is None:
    language = context.Language()

if rights is None:
    rights = context.Rights()

try:  
    context.editMetadata( title=title
                        , description=description
                        , subject=subject
                        , contributors=contributors
                        , effective_date=effective_date
                        , expiration_date=expiration_date
                        , format=format
                        , language=language
                        , rights=rights
                        )
    if context.REQUEST.get( 'change_and_edit', 0 ):
        action_id = 'edit'
    elif context.REQUEST.get( 'change_and_view', 0 ):
        action_id = 'view'
    else:
        action_id = 'metadata'

    action_path = context.getTypeInfo().getActionById( action_id )
    context.REQUEST['RESPONSE'].redirect(
              '%s/%s?portal_status_message=Metadata+changed.'
                % ( context.absolute_url(), action_path ) )
except Exception, msg:
    target_action = context.getTypeInfo().getActionById( 'metadata' )
    context.REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (
                                                                          context.absolute_url()
                                                                        , target_action
                                                                        , msg
                                                                         ))
