CMFUid Readme

    CMFUid introduces a unique id implementation to the CMF 1.5.0 and newer.
    
    Implementation
    
        The supplied tools attach the unique ids to the objects. The objects
        do not have to be aware of unique ids.
        
        The current implementation depends on the portal catalog to find an 
        object of a given unique id. The interfaces do not imply the use
        of the catalog (except the IUniqueIdBrainQuery).
        
        Which Tool does What?
        
            The 'portal_uidgenerator' tools responsibility is to generate 
            unique ids. The 'portal_uidannotation' tool is responsible to 
            attach unique ids to a content object. The 'portal_uidhandler' 
            manages registering and accessing unique ids. 
            
            This design was chosen to allow users replacing only parts of
            the functionality without having to understand the whole thing.
        
        Unique Id API
        
            'portal_uidhandler' implementing 'IUniqueIdHandler' is the main 
            API for playing with unique ids.
        
    Dependencies
    
        Object lookup by unique id depends on CMFCore (especially on 
        portal_catalog). 
    
    Usage
    
        'portal_uidhandler' fully implements IUniqueIdHandler (IUniqueIdSet
        for registering/unregistering unique ids, IUniqueIdQuery for queries
        and IUniqueIdBrainQuery for more efficient queries by returning 
        catalog brains instead of objects).
        
        Have a look at the interfaces.
        
        CMFUid's functionality is used by CMFDefault's favorite content type 
        to follow linked objects. The favorite content type works as before if 
        CMFUid is not installed. 
        
        See 'CMFDefault.Favorite.Favorite'.
    
    gregweb/2004-08-05
