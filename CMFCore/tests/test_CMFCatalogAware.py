##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for CMFCatalogAware.

$Id$
"""

import unittest
import Testing

try:
    import Zope2
except ImportError:
    # BBB: for Zope 2.7
    import Zope as Zope2
Zope2.startup()

from zExceptions import NotFound
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from Products.ZCatalog import CatalogBrains
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware


def physicalpath(ob):
    return '/'.join(ob.getPhysicalPath())


class SimpleFolder(Folder):
    def __init__(self, id):
        self._setId(id)

class DummyRoot(SimpleFolder):
    def getPhysicalRoot(self):
        return self

class DummyOldBrain:
    def __init__(self, ob, path):
        self.ob = ob
        self.id = ob.getId()
        self.path = path
    def getPath(self):
        return self.path
    def getObject(self):
        if self.id == 'missing':
            if self.ob.GETOBJECT_RAISES:
                raise NotFound("missing")
            else:
                return None
        if self.id == 'hop':
            raise ValueError("security problem for this object")
        return self.ob

class DummyBrain(DummyOldBrain):
    def _unrestrictedGetObject(self):
        if self.id == 'missing':
            return self.getObject()
        return self.ob

class DummyCatalog(SimpleItem):
    brain_class = DummyBrain
    def __init__(self):
        self.log = []
        self.obs = []
    def indexObject(self, ob):
        self.log.append('index %s' % physicalpath(ob))
    def reindexObject(self, ob, idxs=[], update_metadata=0):
        self.log.append('reindex %s %s' % (physicalpath(ob), idxs))
    def unindexObject(self, ob):
        self.log.append('unindex %s' % physicalpath(ob))
    def setObs(self, obs):
        self.obs = [(ob, physicalpath(ob)) for ob in obs]
    def unrestrictedSearchResults(self, path):
        res = []
        for ob, obpath in self.obs:
            if not (obpath+'/').startswith(path+'/'):
                continue
            if obpath == path:
                # Normal PathIndex skips initial value
                continue
            res.append(self.brain_class(ob, obpath))
        return res


class TheClass(CMFCatalogAware, Folder):
    def __init__(self, id):
        self._setId(id)
        self.notified = False
    def notifyModified(self):
        self.notified = True


class CMFCatalogAwareTests(unittest.TestCase):

    def setUp(self):
        self.root = DummyRoot('')
        self.root.site = SimpleFolder('site')
        self.site = self.root.site
        self.site._setObject('portal_catalog', DummyCatalog())
        self.site.foo = TheClass('foo')

    def test_indexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.indexObject()
        self.assertEquals(cat.log, ["index /site/foo"])

    def test_unindexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.unindexObject()
        self.assertEquals(cat.log, ["unindex /site/foo"])

    def test_reindexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.reindexObject()
        self.assertEquals(cat.log, ["reindex /site/foo []"])
        self.assert_(foo.notified)

    def test_reindexObject_idxs(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.reindexObject(idxs=['bar'])
        self.assertEquals(cat.log, ["reindex /site/foo ['bar']"])
        self.failIf(foo.notified)

    def test_reindexObjectSecurity(self):
        foo = self.site.foo
        self.site.foo.bar = TheClass('bar')
        bar = self.site.foo.bar
        self.site.foo.hop = TheClass('hop')
        hop = self.site.foo.hop
        cat = self.site.portal_catalog
        cat.setObs([foo, bar, hop])
        foo.reindexObjectSecurity()
        l = list(cat.log)
        l.sort()
        self.assertEquals(l, [
            "reindex /site/foo ['allowedRolesAndUsers']",
            "reindex /site/foo/bar ['allowedRolesAndUsers']",
            "reindex /site/foo/hop ['allowedRolesAndUsers']",
            ])
        self.failIf(foo.notified)
        self.failIf(bar.notified)
        self.failIf(hop.notified)

    def test_reindexObjectSecurity_oldbrain(self):
        self.site.portal_catalog.brain_class = DummyOldBrain
        foo = self.site.foo
        self.site.foo.bar = TheClass('bar')
        bar = self.site.foo.bar
        self.site.foo.hop = TheClass('hop')
        hop = self.site.foo.hop
        cat = self.site.portal_catalog
        cat.setObs([foo, bar, hop])
        foo.reindexObjectSecurity()
        l = list(cat.log)
        l.sort()
        self.assertEquals(l, [
            "reindex /site/foo ['allowedRolesAndUsers']",
            "reindex /site/foo/bar ['allowedRolesAndUsers']",
            "reindex /site/foo/hop ['allowedRolesAndUsers']",
            ])
        self.failIf(foo.notified)
        self.failIf(bar.notified)
        self.failIf(hop.notified)

    def test_reindexObjectSecurity_missing_raise(self):
        # Exception raised for missing object (Zope 2.8 brains)
        foo = self.site.foo
        missing = TheClass('missing').__of__(foo)
        missing.GETOBJECT_RAISES = True
        cat = self.site.portal_catalog
        cat.setObs([foo, missing])
        self.assertRaises(NotFound, foo.reindexObjectSecurity)

    def test_reindexObjectSecurity_missing_noraise(self):
        # Raising disabled
        foo = self.site.foo
        missing = TheClass('missing').__of__(foo)
        missing.GETOBJECT_RAISES = False
        cat = self.site.portal_catalog
        cat.setObs([foo, missing])
        foo.reindexObjectSecurity()
        self.assertEquals(cat.log,
                          ["reindex /site/foo ['allowedRolesAndUsers']"])
        self.failIf(foo.notified)
        self.failIf(missing.notified)

    def test_reindexObjectSecurity_missing_oldbrain(self):
        # Missing object is swallowed by old Zope brains
        self.site.portal_catalog.brain_class = DummyOldBrain
        foo = self.site.foo
        missing = TheClass('missing').__of__(foo)
        missing.GETOBJECT_RAISES = True
        cat = self.site.portal_catalog
        cat.setObs([foo, missing])
        foo.reindexObjectSecurity()
        self.assertEquals(cat.log,
                          ["reindex /site/foo ['allowedRolesAndUsers']"])
        self.failIf(foo.notified)
        self.failIf(missing.notified)

    # FIXME: more tests needed

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFCatalogAwareTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
