from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFDefault import DiscussionItem

def update_discussion(self):
    """
     1. Install (if it isn't there already) a type information
        object for DiscussionItems, so that they can get actions,
        etc.  Erase the "(default)" workflow bound to it, to prevent
        showing the "Retract" options, etc.

     2. Update all DiscussionItems to use the new marking for
        'in_reply_to':

          - Items which are replies to the containing content object
            have None as their 'in_reply_to';

          - Items which are replies to sibling items have the sibling's
            ID as their 'in_reply_to'.

        The representation we are converting from was:

          - Items which are replies to the containing content object
            have the portal-relative pathstring of the content object
            as their 'in_reply_to';

          - Items which are replies to sibling items have the absolute
            path of the sibling as their 'in_reply_to'.
    """

    log = []
    a = log.append
    types_tool = self.portal_types
    if not getattr( types_tool, 'Discussion Item', None ):

        fti = FactoryTypeInformation(
                                **DiscussionItem.factory_type_information[0] )
        types_tool._setObject( 'Discussion Item', fti )
        a( 'Added type object for DiscussionItem' )

        workflow_tool = self.portal_workflow
        workflow_tool.setChainForPortalTypes( ( 'Discussion Item', ), () )
        a( 'Erased workflow for DiscussionItem' )

    items = self.portal_catalog.searchResults( meta_type='Discussion Item' )
    a( 'DiscussionItems updated:' )

    for item in items:

        object = item.getObject()
        talkback = object.aq_parent
        path = item.getPath()
        in_reply_to = object.in_reply_to

        if in_reply_to is None: # we've been here already
            continue

        irt_elements = in_reply_to.split('/')

        if len( irt_elements ) == 1:
            if talkback._container.get( irt_elements[0] ):
                # we've been here already
                continue

        if irt_elements[0] == '': # absolute, so we are IRT a sibling
            sibling_id = irt_elements[ -1 ]
            if talkback._container.get( sibling_id, None ):
                in_reply_to = sibling_id
            else:
                in_reply_to = None
        else:
            in_reply_to = None

        object.in_reply_to = in_reply_to
        assert object.inReplyTo() # sanity check
        object.reindexObject()

        a( path )

    return '\n'.join(log)

