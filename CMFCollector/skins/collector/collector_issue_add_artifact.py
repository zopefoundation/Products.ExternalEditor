## Script (Python) "collector_issue_add_artifacts.py"
##parameters=id, type, description, file
##title=Submit a Request

from Products.PythonScripts.standard import html_quote, url_quote_plus

typeinfo = context.portal_types.getTypeInfo('Collector Issue')
artifacts = typeinfo.getActionById('artifacts')

context.add_artifact(id, type, description, file)

msg = url_quote_plus("'%s' added ..." % id)

context.REQUEST.RESPONSE.redirect("%s/%s?%s" %
                                  (context.absolute_url(), artifacts, msg))
