## Script (Python) "discussion_reply"
##parameters=title,text,Creator
##title=Reply to content

replyID = context.createReply( title = title
                             , text = text
                             , Creator = Creator
                             )

target = '%s/%s' % (context.absolute_url(), replyID)

context.REQUEST.RESPONSE.redirect(target)

