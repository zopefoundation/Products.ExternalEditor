import UserDict

class fakeResponse:
 
    def setStatus(self, status, reason=None):
        pass

    def setHeader(self, name, value, literal=0):
        pass
    
class fakeRequest(UserDict.UserDict):

    def get_header(self, name, default=None):
        pass

