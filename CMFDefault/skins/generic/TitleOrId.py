## Script (Python) "TitleOrId"
##parameters=dontCall=1
##bind namespace=_
##title=Return Title or getId
if not dontCall:
    title = context.Title
    id = context.id
else:
    title = context.Title()
    id = context.getId()
if title:
    return title 
else:
    return id 
