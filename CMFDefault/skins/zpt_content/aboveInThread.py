## Script (Python) "aboveInThread"
##parameters=
##title=Discussion parent breadcrumbs

breadcrumbs = ''
parents = context.parentsInThread()

if parents:
    breadcrumbs = 'Above in thread: '
    for parent in parents:
        p_str = '<a href="%s">%s</a>' % (parent.absolute_url(), parent.Title())
        breadcrumbs = breadcrumbs + p_str + ':'

    breadcrumbs = breadcrumbs[:-1] + '<p>'
        
return breadcrumbs

