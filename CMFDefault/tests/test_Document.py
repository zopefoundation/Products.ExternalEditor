import unittest, string
from Products.CMFDefault.Document import Document
#" 
DOCTYPE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'''

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

ENTITY_IN_TITLE = '''\
<html>
 <head>
  <title>&Auuml;rger</title>
 </head>
 <bOdY>
  <h2>Not a lot here either</h2>
 </bodY>
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
        assert d.text_format == 'structured-text'

    def test_BasicHtml(self):
        d = Document('foo', text=BASIC_HTML)
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

    def test_EntityInTitle(self):
        d = Document('foo')
        d.edit(text_format='html', text=ENTITY_IN_TITLE)
        assert d.title == '&Auuml;rger', "Title '%s' being lost" % (
            d.title )

    def test_HtmlWithDoctype(self):
        d = Document('foo')
        html = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.edit(text_format='', text=html)
        assert d.Description() == 'Describe me'

    def test_HtmlWithoutNewlines(self):
        d = Document('foo')
        html = string.join(string.split(BASIC_HTML, '\n'), '')
        d.edit(text_format='', text=html)
        assert d.Format() == 'text/html'
        assert d.Description() == 'Describe me'

    def test_StructuredText(self):
        d = Document('foo')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0

    def test_Init(self):
        d = Document('foo', text=BASIC_STRUCTUREDTEXT)
        assert d.Format() == 'text/plain'
        assert d.Title() == 'My Document'
        assert d.Description() == 'A document by me'
        assert len(d.Contributors()) == 3
        assert string.find(d.cooked_text, '<p>') >= 0

        d = Document('foo', text=BASIC_HTML)
        assert d.Format() == 'text/html'
        assert d.Title() == 'Title in tag'
        assert len(d.Contributors()) == 2

        d = Document('foo', title='Foodoc')
        assert d.text == ''
        assert d.title == 'Foodoc'
        assert d.Format() == 'text/plain'



def test_suite():
    return unittest.makeSuite(TestCase)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__': main()
