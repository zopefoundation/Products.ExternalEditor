## Script (Python) "collector_issue_edit.py"
##title=Submit a Request

from Products.PythonScripts.standard import url_quote_plus

reqget = context.REQUEST.get

was_security_related = context.security_related

changed = context.edit(title=reqget('title'),
                       security_related=reqget('security_related', 0),
                       description=reqget('description'),
                       topic=reqget('topic'),
                       classification=reqget('classification'),
                       importance=reqget('importance'),
                       severity=reqget('severity'),
                       reported_version=reqget('reported_version'),
                       other_version_info=reqget('other_version_info'),
                       text=reqget('text'))

if context.security_related != was_security_related:
    # Do first available restrict/unrestrict action:
    for action, pretty in context.valid_actions_pairs():
        if pretty in ['Restrict', 'Unrestrict']:
            context.do_action(action, ' Triggered by security_related toggle.')
            changed = changed + ", " + pretty.lower() + 'ed'
            break

whence = context.absolute_url()

if changed:
    msg = url_quote_plus("Changed: " + changed)
    context.REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                      % (whence, msg))

else:
    context.REQUEST.RESPONSE.redirect(whence)

