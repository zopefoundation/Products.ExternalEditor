## Script (Python) "collector_subject_attrs.py"
##parameters=item
##title=Convert consolidated catalog-index Subject tuple into field/value-strings dict

from string import split

got = {}
for i in item.Subject:
    name, val = split(i, ':')
    got[name] = val

return got
