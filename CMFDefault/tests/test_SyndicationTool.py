from unittest import TestCase, TestSuite, makeSuite, main

from DateTime.DateTime import DateTime
from Products.CMFCore.tests.base.testcase import SecurityTest

class Dummy:
    def getId(self):
        return 'dummy'

class SyndicationToolTests(SecurityTest):

    def _getTargetClass(self):
        from Products.CMFDefault.SyndicationTool import SyndicationTool
        return SyndicationTool

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_empty(self):
        ONE_MINUTE = (24.0 * 60.0) / 86400

        tool = self._makeOne()

        self.assertEqual(tool.syUpdatePeriod, 'daily')
        self.assertEqual(tool.syUpdateFrequency, 1)
        self.failUnless(DateTime() - tool.syUpdateBase < ONE_MINUTE)
        self.failIf(tool.isAllowed)
        self.assertEqual(tool.max_items, 15)

    def test_editProperties_normal(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.editProperties(updatePeriod=PERIOD,
                            updateFrequency=FREQUENCY,
                            updateBase=NOW,
                            isAllowed=True,
                            max_items=MAX_ITEMS,
                           )

        self.assertEqual(tool.syUpdatePeriod, PERIOD)
        self.assertEqual(tool.syUpdateFrequency, FREQUENCY)
        self.assertEqual(tool.syUpdateBase, NOW)
        self.failUnless(tool.isAllowed)
        self.assertEqual(tool.max_items, MAX_ITEMS)

    def test_editProperties_coercing(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.editProperties(updatePeriod=PERIOD,
                            updateFrequency='%d' % FREQUENCY,
                            updateBase=NOW.ISO(),
                            isAllowed='True',
                            max_items='%d' % MAX_ITEMS,
                           )

        self.assertEqual(tool.syUpdatePeriod, PERIOD)
        self.assertEqual(tool.syUpdateFrequency, FREQUENCY)
        self.assertEqual(tool.syUpdateBase, DateTime(NOW.ISO()))
        self.failUnless(tool.isAllowed)
        self.assertEqual(tool.max_items, MAX_ITEMS)

    def test_editSyInformationProperties_disabled(self):
        from zExceptions import Unauthorized

        tool = self._makeOne()
        dummy = Dummy()
        try:
            tool.editSyInformationProperties(object, updateFrequency=1)
        except Unauthorized:
            raise
        except: # WAAA! it raises a string!
            pass
        else:
            assert 0, "Didn't raise"

    def test_editSyInformationProperties_normal(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        dummy = Dummy()
        info = dummy.syndication_information = Dummy()

        tool.editSyInformationProperties(dummy,
                                         updatePeriod=PERIOD,
                                         updateFrequency=FREQUENCY,
                                         updateBase=NOW,
                                         max_items=MAX_ITEMS,
                                        )

        self.assertEqual(info.syUpdatePeriod, PERIOD)
        self.assertEqual(info.syUpdateFrequency, FREQUENCY)
        self.assertEqual(info.syUpdateBase, NOW)
        self.assertEqual(info.max_items, MAX_ITEMS)

    def test_editSyInformationProperties_coercing(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        dummy = Dummy()
        info = dummy.syndication_information = Dummy()

        tool.editSyInformationProperties(dummy,
                                         updatePeriod=PERIOD,
                                         updateFrequency='%d' % FREQUENCY,
                                         updateBase=NOW.ISO(),
                                         max_items='%d' % MAX_ITEMS,
                                        )

        self.assertEqual(info.syUpdatePeriod, PERIOD)
        self.assertEqual(info.syUpdateFrequency, FREQUENCY)
        self.assertEqual(info.syUpdateBase, DateTime(NOW.ISO()))
        self.assertEqual(info.max_items, MAX_ITEMS)

def test_suite():
    return TestSuite((
        makeSuite(SyndicationToolTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

