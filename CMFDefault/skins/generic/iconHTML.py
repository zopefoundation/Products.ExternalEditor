## Script (Python) "iconHTML"
##bind namespace=_
##title=Returns the HTML for the current object's icon, if it is available
##parameters=

# dont you just wish namespaces had a get(name,default) method?! ;-)
try:
    iconURL=_['getIcon']
except KeyError:
    try:
        iconURL=_['icon']
    except:
        iconURL=''

if iconURL:
    try:
        Type = _['Type']
    except:
        Type=''
    return '<img src="%s" align="left" alt="%s" border="0"/>' % (iconURL,
                                                                 Type)

return ''
