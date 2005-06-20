##title=Submit a Request
##
collector = context.aq_parent
try:
    target = collector.getActionInfo('object/addissue')['url']
except AttributeError:
    # for usage with CMF < 1.5
    ti = collector.getTypeInfo()
    target = "%s/%s" % ( collector.absolute_url(),
                         ti.getActionById('addissue') )

context.REQUEST.RESPONSE.redirect(target)
