## Script (Python) "doFormSearch"
##parameters=REQUEST
##title=Pre-process form variables, then return catalog query results.
##
form_vars = {}
select_vars = ( 'review_state'
              , 'Subject'
              , 'created'   
              , 'Type'
              )

for k, v in REQUEST.form.items():

    if k in select_vars:

        if same_type( v, [] ):
            v = filter( None, v )
        if not v:
            continue

    form_vars[ k ] = v

return context.portal_catalog( form_vars )
