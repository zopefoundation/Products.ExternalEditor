""" Interfaces:  IUser, IUserFolder, IMutableUserFolder, IEnumerableUserFolder

$Id$
"""

from Interface import Interface
from AccessControl.ZopeSecurityPolicy import _noroles


class IBasicUser( Interface ):

    """ Specify the interface called out in AccessControl.User.BasicUser
        as the "Public User object interface", except that '_getPassword'
        is *not* part of the contract!
    """

    def getId():

        """ Get the ID of the user.
        
        o The ID can be used, at least from Python, to get the user from
          the user's UserDatabase
        """

    def getUserName():

        """ Return the name used by the user to log into the system.

        o Note that this may not be identical to the user's 'getId'
          (to allow users to change their login names without changing
          their identity).
        """

    def getRoles():

        """ Return the roles assigned to a user "globally".
        """

    def getRolesInContext( object ):

        """ Return the roles assigned to the user in context of 'object'.

        o Roles include both global roles (ones assigned to the user
          directly inside the user folder) and local roles (assigned
          in context of the passed in object.
        """

    def getDomains():

        """ Return the list of domain restrictions for a user.
        """


class IUserFolder( Interface ):

    """ Specify the interface called out in AccessControl.User.BasicUserFolder
        as the "Public UserFolder object interface":
        
    o N.B: "enumeration" methods ('getUserNames', 'getUsers') are *not*
           part of the contract!  See IEnumerableUserFolder.
    """

    def getUser( name ):

        """ Return the named user object or None.
        """

    def getUserById( id, default=None ):

        """ Return the user corresponding to the given id.

        o If no such user can be found, return 'default'.
        """

    def validate( request, auth='', roles=_noroles ):

        """ Perform identification, authentication, and authorization.

        o Return an IUser-conformant user object, or None if we can't
          identify / authorize the user.

        o 'request' is the request object

        o 'auth' is any credential information already extracted by
          the caller

        o roles is the list of roles the caller 
        """

class IMutableUserFolder( Interface ):

    """ Specify the interface called out in AccessControl.User.BasicUserFolder
        as the "Public UserFolder object interface":
        
    o N.B: "enumeration" methods ('getUserNames', 'getUsers') are *not*
           part of the contract!  See IEnumerableUserFolder.
    """

    def userFolderAddUser( name, password, roles, domains, **kw ):

        """ Create a new user object.
        """

    def userFolderEditUser( name, password, roles, domains, **kw ):

        """ Change user object attributes.
        """

    def userFolderDelUsers( names ):

        """ Delete one or more user objects.
        """

class IEnumerableUserFolder( IUserFolder ):

    """ Interface for user folders which can afford to enumerate their users.
    """

    def getUserNames():

        """ Return a list of usernames.
        """

    def getUsers():

        """ Return a list of user objects.
        """
