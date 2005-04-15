from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass
import Acquisition

from Products.CMFCore.MemberDataTool import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberData


class DummyUserFolder(Acquisition.Implicit):

    def __init__(self):
        self._users = {}

    def _addUser(self, user):
        self._users[user.getUserName()] = user

    def userFolderEditUser(self, name, password, roles, domains):
        user = self._users[name]
        if password is not None:
            user.__ = password
        # Emulate AccessControl.User's stupid behavior (should test None)
        user.roles = tuple(roles)
        user.domains = tuple(domains)


class DummyUser(Acquisition.Implicit):

    def __init__(self, name, password, roles, domains):
        self.name = name
        self.__ = password
        self.roles = tuple(roles)
        self.domains = tuple(domains)

    def getUserName(self):
        return self.name

    def getRoles(self):
        return self.roles + ('Authenticated',)

    def getDomains(self):
        return self.domains


class DummyMemberDataTool(Acquisition.Implicit):
    pass


class MemberDataToolTests(TestCase):

    def test_deleteMemberData(self):
        tool = MemberDataTool()
        tool.registerMemberData('Dummy', 'user_foo')
        self.failUnless( tool._members.has_key('user_foo') )
        self.failUnless( tool.deleteMemberData('user_foo') )
        self.failIf( tool._members.has_key('user_foo') )
        self.failIf( tool.deleteMemberData('user_foo') )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import portal_memberdata as IMemberDataTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IMemberDataTool, MemberDataTool)
        verifyClass(IActionProvider, MemberDataTool)

class MemberDataTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_memberdata \
                import MemberData as IMemberData

        verifyClass(IMemberData, MemberData)

    def test_setSecurityProfile(self):
        mdtool = DummyMemberDataTool()
        aclu = DummyUserFolder()
        user = DummyUser('bob', 'pw', ['Role'], ['domain'])
        aclu._addUser(user)
        user = user.__of__(aclu)
        member = MemberData(None, 'bob').__of__(mdtool).__of__(user)
        member.setSecurityProfile(password='newpw')
        self.assertEqual(user.__, 'newpw')
        self.assertEqual(list(user.roles), ['Role'])
        self.assertEqual(list(user.domains), ['domain'])
        member.setSecurityProfile(roles=['NewRole'])
        self.assertEqual(user.__, 'newpw')
        self.assertEqual(list(user.roles), ['NewRole'])
        self.assertEqual(list(user.domains), ['domain'])
        member.setSecurityProfile(domains=['newdomain'])
        self.assertEqual(user.__, 'newpw')
        self.assertEqual(list(user.roles), ['NewRole'])
        self.assertEqual(list(user.domains), ['newdomain'])

def test_suite():
    return TestSuite((
        makeSuite( MemberDataToolTests ),
        makeSuite( MemberDataTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
