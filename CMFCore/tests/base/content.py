DOCTYPE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'''

HTML_TEMPLATE = '''\
<html><head>
 <title>%(title)s</title>
</head>
<body bgcolor="#efe843">%(body)s</body>
</html>
'''

SIMPLE_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

BASIC_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
  <meta name="keywords" content="unit tests, framework; ,zope ">
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

SIMPLE_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

BASIC_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope
Keywords: unit tests; , framework

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

STX_WITH_HTML = """\
Sometimes people do interesting things

  Sometimes people do interesting things like have examples
  of HTML inside their structured text document.  We should
  be detecting that this is indeed a structured text document
  and **NOT** an HTML document::

    <html>
    <head><title>Hello World</title></head>
    <body><p>Hello world, I am Bruce.</p></body>
    </html>

  All in favor say pi!
"""


STX_NO_HEADERS = """\
Title Phrase

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""

STX_NO_HEADERS_BUT_COLON = """\
Plain STX:  No magic!

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""
