## Script (Python) "discussion_reply"
##parameters=title,text
##title=Reply to content

replyID = context.createReply( title = title
                             , text = text
                             )

target = '%s/%s' % (context.absolute_url(), replyID)

context.REQUEST.RESPONSE.redirect(target)

