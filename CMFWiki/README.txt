This is the CMFWiki product.  CMFWiki requires the Zope CMF.

It contains code from the ZWiki product, but it is otherwise unrelated. You
needn't have ZWiki installed to use CMFWiki.

To use the product, you'll need to register the CMFWikiPage and CMFWiki
types in the portal types tool.  You'll also need to add a Filesystem
Directory View to the skins tool for the skins contained within this
pacakge, and place the directory view in the skins path for the skins you're
intending to use.  You'll also probably want to remove workflow
for CMFWikis and CMFWikiPages.  The "Install" script in this product's
Extensions directory does these things for you.  Read the script
for details on how to install CMFWiki.

- Chris McDonough (chrism@digicool.com)
