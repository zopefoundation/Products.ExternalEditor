## Script (Python) "wikipage_create_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=page,text,log=''
##title=
##
context.create_page( page, text, log )
context.REQUEST['RESPONSE'].redirect( context.wiki_page_url()
                                    + '?portal_status_message=Page+added.' )
