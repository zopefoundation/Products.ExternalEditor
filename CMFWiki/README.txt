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

As with WikiForNow, CMFWiki is an expedient, to enable communication
in and about our development processes.  We're going to continue to
use it, but our development efforts will be invested in generalizing
the useful features for all relevant CMF content, rather than in
supporting and developing the wiki.  What this means is that we will
not be maintaining CMFWiki as a supported product.

That said (for those of you who've read this far!-), we *are* making
it available in the CMF section of our cvs repository, as the CMFWiki
subdirectory.  Like i said, it's unmaintained, and we have to keep
work on it to the minimum necessary to keep it usable for our own
purposes.  Among other things, this means that any distributions
beyond CVS (eg, tarballs) will have to come from the community.  We
make no guarantees about pursing fixes, etc.

One important note for use with Zope pre v2.4.  CMFWiki was developed
for that version, and depends on a new feature where every
authenticated user intrinsically has the 'Authenticated' role.  In
order for the non-anonymous regulation category to work with pre-2.4
Zope, all your users have to have this additional role added.  (If
someone were to contribute a hotfix to make this automatic, we might
include it with the CMFWiki product.)

Finally, for any of you running "WikiForNow wikis",
http://dev.zope.org/Wikis/DevSite/Projects/WikiForNow , there's a
conversion script, CMFWiki/Extensions/migrate.py .  See the docstring
for the do_site function for instructions.  (I haven't yet tried
running it as an extension method, just from the zeo/python prompt,
but i expect it will work either way.)

Ken
klm@digicool.com
