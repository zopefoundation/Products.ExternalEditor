## Script (Python) "isDiscussable"
##title=Return whether the context is discussable or not.
##parameters=
if hasattr(context, 'allow_discussion'):
    return context.allow_discussion
else:
    return None
