from unittest import TestCase

from OFS.Image import Pdata

from ..ExternalEditor import PDataStreamIterator


class Tests(TestCase):
    def test_empty(self):
        si = PDataStreamIterator(None)
        self.assertEqual(list(si), [])

    def test_chained(self):
        d = Pdata(b"abc")
        d.next = Pdata(b"def")
        si = PDataStreamIterator(d)
        self.assertEqual(list(si), [b"abc", b"def"])
