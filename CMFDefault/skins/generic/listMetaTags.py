## Script (Python) "listMetaTags"
##parameters=
##title=List Dublin Core for '<meta>' tags
##
hdrlist = []

#   These two are import for most search engines
hdrlist.append( ( 'description', context.Description() ) )
hdrlist.append( ( 'keywords', ', '.join( context.Subject() ) ) )

hdrlist.append( ( 'DC.description', context.Description() ) )
hdrlist.append( ( 'DC.subject', ', '.join( context.Subject() ) ) )
hdrlist.append( ( 'DC.creator', context.Creator() ) )
hdrlist.append( ( 'DC.contributors', ', '.join( context.Contributors() ) ) )

if context.Publisher() != 'No publisher':
    hdrlist.append( ( 'DC.publisher', context.Publisher() ) )

created = context.CreationDate()

#   Filter out DWIMish artifacts on effective / expiration dates
effective = context.effective_date
eff_str = ( effective and effective.year() > 1000
                      and effective != created ) and effective.Date() or ''

expires = getattr( context, 'expiration_date', None )
exp_str = ( expires and expires.year() < 9000 ) and expires.Date() or ''

hdrlist.append( ( 'DC.date.created', created ) )
hdrlist.append( ( 'DC.date.modified', context.ModificationDate() ) )

if exp_str or exp_str:
    hdrlist.append( ( 'DC.date.valid_range'
                    , '%s - %s' % ( eff_str, exp_str ) ) )

hdrlist.append( ( 'DC.type', context.Type() ) )
hdrlist.append( ( 'DC.format', context.Format() ) )
hdrlist.append( ( 'DC.language', context.Language() ) )
hdrlist.append( ( 'DC.rights', context.Rights() ) )

# Strip empty values
return filter( lambda x: x[1], hdrlist ) 
