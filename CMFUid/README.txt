Unique id Readme

    CMFUid introduces a unique id implementation to the CMF (from the 
    beginning of CMF 1.5).
    
    Implementation
    
        The supplied tools attach the unique ids to the objects. The objects
        do not have to be aware of unique ids.
        
        The current implementation depends on the portal catalog to find an 
        object of a given unique id. The interfaces do not imply the use
        of the catalog (except the IUniqueIdBrainQuery).
        
        The 'portal_uidgenerator' tools responsibility is to generate unique
        ids. The 'portal_uidhandler' manages registering and accessing unique
        ids. It's the tool through that applications are accessing unique ids.
        
    Dependencies
    
        Object lookup by unique id depends on the portal_catalog
    
    Usage
    
        'portal_uidhandler' fully implements IUniqueIdHandler (IUniqueIdSet
        for registering/unregistering unique ids, IUniqueIdQuery for queries
        and IUniqueIdBrainQuery for more efficient querying).
        
