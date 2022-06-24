import Testing.testbrowser
import Testing.ZopeTestCase
import Zope2.App


class ZMITests(Testing.ZopeTestCase.FunctionalTestCase):
    """Testing the ZMI rendering."""

    def setUp(self):
        super(ZMITests, self).setUp()

        Zope2.App.zcml.load_site(force=True)

        uf = self.app.acl_users
        uf.userFolderAddUser('manager', 'manager_pass', ['Manager'], [])
        self.app.manage_addProduct['OFSP'].addDTMLMethod('meth')

    def test_ZMI(self):
        """It renders a link to to external edit."""
        browser = Testing.testbrowser.Browser()
        browser.login('manager', 'manager_pass')
        browser.open('http://localhost/manage_main')
        link = browser.getLink(url='meth.zem')
        self.assertEqual(link.attrs['title'], 'Edit using external editor')
        self.assertEqual(link.url, 'http://localhost/externalEdit_/meth.zem')
