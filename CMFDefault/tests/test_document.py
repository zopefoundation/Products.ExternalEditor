import unittest, string
from Products.CMFDefault.Document import Document
#" 
BASIC_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com baz@bam.net">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

BASIC_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com baz@bam.net no@yes.maybe

This is the header

  Body body body body body
  body body body.
'''

class TestCase(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self): pass

    def test_Empty(self):
        d = Document('foo')
        assert d.title == ''
        assert d.description == ''
        assert d.text == ''
        assert d.text_format == ''
        assert d.cooked_text == ''

    def test_BasicHtml(self):
        d = Document('foo')
        d.edit(text_format='', text=BASIC_HTML)
        assert d.Format() == 'text/html'
        assert d.title == 'Title in tag'
        assert string.find(d.text, '</body>') == -1
        assert d.Description() == 'Describe me'
        assert len(d.Contributors()) == 2

    def test_UpperedHtml(self):
        d = Document('foo')
        d.edit(text_format='', text=string.upper(BASIC_HTML))
        assert d.Format() == 'text/html'
        assert d.title == 'TITLE IN TAG'
        assert string.find(d.text, '</BODY') == -1
        assert d.Description() == 'DESCRIBE ME'
        assert len(d.Contributors()) == 2

    def test_StructuredText(self):
        d = Document('foo')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0

def test_suite():
    return unittest.makeSuite(TestCase)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__': main()
