##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from __future__ import print_function
from rfc822 import Message
from StringIO import StringIO

# Load fixture
from Testing import ZopeTestCase
from OFS.SimpleItem import SimpleItem
from Testing.ZopeTestCase.zopedoctest.functional import http

# Install our product
ZopeTestCase.installProduct('ExternalEditor')


class SideEffects(SimpleItem):
    meta_type = 'Side Effects'

    def __init__(self, id, content):
        self.id = id
        self.content = content

    def manage_FTPget(self, REQUEST, RESPONSE):
        RESPONSE.setHeader('Content-Type', 'text/plain')
        return self.content


def print_http(request):
    response = http(request)
    status, _, msg = str(response).partition("\r\n")
    print(status)
    message = Message(StringIO(msg))
    for key, value in sorted(message.items()):
        print('{}: {}'.format(key, value))
    print()
    print(message.fp.read())


def test_suite():
    import unittest
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import doctest
    FileSuite = doctest.FunctionalDocFileSuite
    files = [
        'link.txt',
        'edit.txt',
    ]
    for f in files:
        suite.addTest(
            FileSuite(f, package='Products.ExternalEditor.tests',
                      globs={'print_http': print_http}))
    return suite
