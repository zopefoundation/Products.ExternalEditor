## Script (Python) "subjectsList"
##title=List Subjects for Metadata Editing
allowedSubjects=container.portal_metadata.listAllowedSubjects(context)
item=[]
for i in context.Subject():
    if not i in allowedSubjects:
        item.append(i)
return item
