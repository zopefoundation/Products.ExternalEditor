## Script (Python) "folder_rename_items"
##title=Objects for folder_rename_form
##parameters=

ids = filter(lambda id,c=context.aq_explicit: hasattr(c,id),
             context.REQUEST.get('ids',[]))

objects = map(lambda id,c=context: getattr(c,id),ids)

return filter(lambda ob: ob.cb_isMoveable(),
                 objects)
