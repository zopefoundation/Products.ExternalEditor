## Script (Python) "topic_addCriterion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, field, criteria_type
##title=
##

context.addCriteria(field=field, criteria_type=criteria_type)

RESPONSE.redirect('%s/topic_criteria_form' % context.absolute_url())
