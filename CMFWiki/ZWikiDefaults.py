from DocumentTemplate import HTML

# built-in defaults - to override these, define any of the following
# DTML methods(/python methods/properties ?):
#
# standard_wiki_header
# standard_wiki_footer
# standard_wiki_page
# editform
# backlinks
# titleprefix

# ? the ramifications of when and where this dtml gets executed are
# not yet clear ...

# would like to move these to separate files.. how do I define
# these in such a way that "<dtml-var id>" will work at runtime ?
#
# also would prefer not to inline the header in editform & backlinks
#
#default_wiki_page =   HTMLFile('default_wiki_page', globals())
#default_wiki_header = HTMLFile('default_wiki_header', globals())
#default_wiki_footer = HTMLFile('default_wiki_footer', globals())
#default_editform =    HTMLFile('default_editform', globals())
#default_backlinks =   HTMLFile('default_backlinks', globals())

#####################################################################
default_wiki_page = HTML(source_string=
'''Describe <dtml-var page> here
''')
#####################################################################
default_wiki_header = HTML(source_string=
'''<dtml-if standard_html_header>
  <dtml-var standard_html_header>
<dtml-else>
  <HTML>
  <HEAD>
  <TITLE><dtml-var titleprefix missing> <dtml-var id> of 
         <dtml-with aq_parent><dtml-var id></dtml-with>
         <dtml-var id></TITLE>
  </HEAD>
  <BODY BGCOLOR="#FFFFFF">
</dtml-if>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr>
    <td> <small>
      <dtml-with aq_parent><dtml-var id></dtml-with>
        <a href="&dtml-wiki_page_url;/map#&dtml-id;">Table of Contents</a>
         </small>
    </td>
    <td align="right">
        <small>
          Last 
          <a href="&dtml-wiki_page_url;/pagehistory">edited</a>
            <dtml-if last_editor> by <b><dtml-var last_editor></b> </dtml-if>
            on <dtml-var bobobase_modification_time fmt=aCommon> </small>
    </td>
  <tr>
</table>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr align="left" bgcolor="eeeeee">
    <td>
      <dtml-var "context(REQUEST, with_siblings=0)">
    </td>
  </tr>
</table>
<!-- end of standard_wiki_header -->

''')
#####################################################################
default_wiki_footer = HTML(source_string=
'''<!-- start of standard_wiki_footer -->

<dtml-let editor="isAllowed('edit', REQUEST=REQUEST)"
      notediting="_.string.find(URL0, 'editform') == -1"
   notcommenting="_.string.find(URL0, 'commentform') == -1"
       commenter="isAllowed('comment', REQUEST=REQUEST)">

  <form method="POST" action="SearchPage">
  <table width="100%" border="0"
         cellspacing="0" cellpadding="5" bgcolor="eeeeee">
    <tr valign="top">
      <td>
        <dtml-if notediting>
          <a href="&dtml-wiki_page_url;/editform"> 
            <dtml-if editor> Edit <dtml-else> View source </dtml-if>
          </a>
        </dtml-if>
        <dtml-if "notcommenting and commenter">
          <dtml-if notediting> or </dtml-if>
            <a href="&dtml-wiki_page_url;/commentform"> Comment on </a>
        </dtml-if>
         <em> <dtml-var id size=30> </em>
        <br>
         <font size="-1">
          Page <a href="&dtml-wiki_page_url;/advancedform">Advanced Actions</a>
          and <a href="&dtml-wiki_page_url;/pagehistory">History</a>
         </font>
        <br>
        Visitor: <em>
        <dtml-var "REQUEST.cookies.get('zwiki_username',
                                   REQUEST.AUTHENTICATED_USER.getUserName())">
        </em>
      </td>
      <td align="right" valign="top">
        <input type="hidden" name="source" value="jump">
        <a href="&dtml-wiki_base_url;/JumpTo">Jump to</a>:
        <input name="expr" type="text" size="20" value="">
      <small>
      <em>
      <br>
      Enter a pagename prefix or search term & press enter.
      <br>See </em><a href="&dtml-wiki_base_url;/SearchPage">SearchPage</a><em>
      for full search,
      </em><a href="&dtml-wiki_base_url;/FrontPage">FrontPage</a><em> for
      orientation.
      </em>
      </small>
      </td>
    </tr>
  </table>
  </form>

  <dtml-if standard_html_footer>
    <dtml-var standard_html_footer>
  <dtml-else>
    </BODY>
    </HTML>
  </dtml-if>
</dtml-let>
''')
#####################################################################
default_editform = HTML(source_string=
'''<dtml-if standard_html_header>
  <dtml-var standard_html_header>
<dtml-else>
  <HTML>
  <HEAD>
  <TITLE><dtml-var titleprefix missing> <dtml-var id> of 
         <dtml-with aq_parent><dtml-var id></dtml-with>
         <dtml-var id></TITLE>
  </HEAD>
  <BODY BGCOLOR="#FFFFFF">
</dtml-if>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr>
    <td> <small>
      <dtml-with aq_parent><dtml-var id></dtml-with>
        <a href="&dtml-wiki_page_url;/map#&dtml-id;">Table of Contents</a>
         </small>
    </td>
    <td align="right">
        <small>
          Last 
          <a href="&dtml-wiki_page_url;/pagehistory">edited</a>
            <dtml-if last_editor> by <b><dtml-var last_editor></b> </dtml-if>
            on <dtml-var bobobase_modification_time fmt=aCommon> </small>
    </td>
  <tr>
</table>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr align="left" bgcolor="eeeeee">
    <td>
      <dtml-var "context(REQUEST, with_siblings=0)">
    </td>
  </tr>
</table>
<!-- end of standard_wiki_header -->

<dtml-comment> ZWiki page edit form, used for editing and creating new pages.
</dtml-comment>

<dtml-let action="(REQUEST.get('action', action))"
      niceaction="((action == 'Create') and 'create') or 'edit'"
          noedit="not isAllowed(niceaction, REQUEST=REQUEST)"
         editcat="opCategory('edit')"
        whichwho="{'nonanon': 'You must be logged-in to',
                   'owners': 'Only the owners may',
                   'nobody': 'Nobody may'}">

  <dtml-if "action == 'Create'">

    <dtml-if noedit> <font color="gray"> </dtml-if>

      <h3> Create <em>&dtml-page;</em> ZWiki Page </h3>

    <dtml-if noedit> </font> </dtml-if>

    <dtml-if noedit>
      <strong> <dtml-var "whichwho[createcat]">
        create new pages from <dtml-var "this().getId()">.
      </strong>
    <dtml-elif doalternate>
      Create this page as a file or an image upload, below.  Use the 
      <a href="&dtml-wiki_page_url;/editform?doalternate=&page=&dtml.url_quote-page;&action=Create">
      regular edit form</a> to create it as a normal ZWiki page, instead.
    <dtml-else>
      Fill in the text and hit the <em> Create <dtml-var id> </em> button.
      Use <a href="&dtml-wiki_page_url;/editform?doalternate=1&page=&dtml.url_quote-page;&action=Create">
      this form</a> to upload the page as a file or image, instead.
    </dtml-if>

  <dtml-else>
    <dtml-comment> Editing, not necessarily allowed to do so. </dtml-comment>

    <h3>
      <dtml-if noedit> View <dtml-else> Edit </dtml-if>
      <em>&dtml-id;</em> ZWiki Page
    </h3>
    <dtml-if noedit>
      <strong> You can view the page source, below, but not edit it. </strong>
      (<dtml-var "whichwho[editcat]"> edit this page.)
    </dtml-if>
    <dtml-if "(action != 'Create') and (id != 'FrontPage')">
      <p> See the 
        <a href="&dtml-wiki_page_url;/advancedform">advanced actions
        form</a> for actions like renaming or deleting the page, or
        changing page policies, and the
        <a href="&dtml-wiki_page_url;/backlinks"> backlinks page</a> for
        reparenting.
    </dtml-if>
  </dtml-if>

  <dtml-if "not ((action == 'Create') and noedit)">

    <dtml-comment> Visitor is either allowed to create the page, or in
                   edit mode, either editing or just viewing.
    </dtml-comment>

    <FORM METHOD="POST"
          ACTION="&dtml-wiki_base_url;/<dtml-var oldid url_quote>/edit"
          ENCTYPE="multipart/form-data">
    <input type=hidden name=timeStamp value="&dtml-editTimestamp;">
    <input type=hidden name=page value="&dtml-id;">

    <table width="100%" border="0" cellspacing="0" cellpadding="5"
           <dtml-if doalternate> bgcolor="eeeeee" </dtml-if> >

     <dtml-if doalternate>
      <tr>
        <td align="right">
          <strong> File </strong>
          <input type="radio" name="filetype" value="file" CHECKED>
          <br> or <strong> Image </strong>
          <input type="radio" name="filetype" value="image">
        </td>
        <td ALIGN="LEFT" VALIGN="middle" colspan=2>
          <INPUT TYPE="file" NAME="file" SIZE="25" VALUE="">
        </td>
      </tr>
      <tr>
        <th ALIGN="right" VALIGN="CENTER"> <EM>Title</EM> </Th>
        <td ALIGN="LEFT" VALIGN="CENTER">
        <INPUT TYPE="TEXT" NAME="title" SIZE="40">
        </td>
        <td colspan=2 align="right" valign="bottom">
          <INPUT TYPE="SUBMIT" name="Create" VALUE="Create File or Image">
        </td>
      </tr>
     <dtml-else>
      <!-- Readonly *and* onkeydown for bowser diversity. -->
      <tr bgcolor=<dtml-if noedit>"pink"<dtml-else>"eeeeee"</dtml-if> >
        <td colspan=2 align="center">
          <TEXTAREA WRAP="soft" NAME="text"
                    ROWS=<dtml-var zwiki_height missing=18>
                    COLS=<dtml-var zwiki_width missing=80>
                  <dtml-if noedit>
                    readonly
                    onkeydown="this.blur(); return false;"
                  </dtml-if>
><dtml-var text html_quote></TEXTAREA>
        </td>
      </tr>
      <tr bgcolor=<dtml-if noedit>"pink"<dtml-else>"eeeeee"</dtml-if> >
        <td valign="middle" align="left">
          See <a href="&dtml-wiki_base_url;/HowDoIEdit">HowDoIEdit</a>
          for help.
          <br> Format: <em> <dtml-var page_type> </em>
        </td>
       <dtml-if noedit>
        <th valign="middle" align="center"> &dtml-action; Disabled
       <dtml-else>
        <td valign="middle" align="right">
          <INPUT TYPE="submit"
                 NAME="<dtml-var action>"
                 VALUE="<dtml-var action> <dtml-var id size=20>">
       </dtml-if>
        </td>
      </tr>
      <dtml-if "not noedit">
       <tr bgcolor="eeeeee">
         <th colspan=2 align="center"> Log Message </td>
       </tr>
       <tr bgcolor="eeeeee">
         <td colspan=2 align="center">
           <TEXTAREA WRAP="soft" NAME="log"
                     ROWS=3
                     COLS=80
></TEXTAREA>
         </td>
       </tr>
       <tr bgcolor="eeeeee">
         <td colspan=2>
           Log for landmark changes - enter a note characterizing your
           change.  It will be connected with the page version,
           exposing the version for browsing in the condensed
           <a href="&dtml-wiki_page_url;/pagehistory">page history</a>.
         </td>
       </tr>
      </dtml-if> <dtml-comment> "not noedit" </dtml-comment>
     </dtml-if> <dtml-comment> doalternate </dtml-comment>
    </table>
   </FORM>
  </dtml-if>
</dtml-let>

<!-- start of standard_wiki_footer -->

<dtml-let editor="isAllowed('edit', REQUEST=REQUEST)"
      notediting="_.string.find(URL0, 'editform') == -1"
   notcommenting="_.string.find(URL0, 'commentform') == -1"
       commenter="isAllowed('comment', REQUEST=REQUEST)">

  <form method="POST" action="SearchPage">
  <table width="100%" border="0"
         cellspacing="0" cellpadding="5" bgcolor="eeeeee">
    <tr valign="top">
      <td>
        <dtml-if notediting>
          <a href="&dtml-wiki_page_url;/editform"> 
            <dtml-if editor> Edit <dtml-else> View source </dtml-if>
          </a>
        </dtml-if>
        <dtml-if "notcommenting and commenter">
          <dtml-if notediting> or </dtml-if>
            <a href="&dtml-wiki_page_url;/commentform"> Comment on </a>
        </dtml-if>
         <em> <dtml-var id size=30> </em>
        <br>
         <font size="-1">
          Page <a href="&dtml-wiki_page_url;/advancedform">Advanced Actions</a>
          and <a href="&dtml-wiki_page_url;/pagehistory">History</a>
         </font>
        <br>
        Visitor: <em>
        <dtml-var "REQUEST.cookies.get('zwiki_username',
                                   REQUEST.AUTHENTICATED_USER.getUserName())">
        </em>
      </td>
      <td align="right" valign="top">
        <input type="hidden" name="source" value="jump">
        <a href="&dtml-wiki_base_url;/JumpTo">Jump to</a>:
        <input name="expr" type="text" size="20" value="">
      <small>
      <em>
      <br>
      Enter a pagename prefix or search term & press enter.
      <br>See </em><a href="&dtml-wiki_base_url;/SearchPage">SearchPage</a><em>
      for full search,
      </em><a href="&dtml-wiki_base_url;/FrontPage">FrontPage</a><em> for
      orientation.
      </em>
      </small>
      </td>
    </tr>
  </table>
  </form>

  <dtml-if standard_html_footer>
    <dtml-var standard_html_footer>
  <dtml-else>
    </BODY>
    </HTML>
  </dtml-if>
</dtml-let>
''')
#####################################################################
default_backlinks = HTML(source_string=
'''<dtml-if standard_html_header>
  <dtml-var standard_html_header>
<dtml-else>
  <HTML>
  <HEAD>
  <TITLE><dtml-var titleprefix missing> <dtml-var id> of 
         <dtml-with aq_parent><dtml-var id></dtml-with>
         <dtml-var id></TITLE>
  </HEAD>
  <BODY BGCOLOR="#FFFFFF">
</dtml-if>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr>
    <td> <small>
      <dtml-with aq_parent><dtml-var id></dtml-with>
        <a href="&dtml-wiki_page_url;/map#&dtml-id;">Table of Contents</a>
         </small>
    </td>
    <td align="right">
        <small>
          Last 
          <a href="&dtml-wiki_page_url;/pagehistory">edited</a>
            <dtml-if last_editor> by <b><dtml-var last_editor></b> </dtml-if>
            on <dtml-var bobobase_modification_time fmt=aCommon> </small>
    </td>
  <tr>
</table>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr align="left" bgcolor="eeeeee">
    <td>
      <dtml-var "context(REQUEST, with_siblings=0)">
    </td>
  </tr>
</table>
<!-- end of standard_wiki_header -->

<h2> Backlinks and Nesting Information </h2>

<form action="reparent">

<a href="../<dtml-var id>"><dtml-var id></a> is linked on the following pages:
<p>

<dtml-if "not isAllowed('move', REQUEST)">
 <font color="gray"> (You're not allowed to change this page's lineage) </font>
<br>
</dtml-if>

<dtml-let thispage=id
       thisparents=parents
     maybedisabled="((not isAllowed('move', REQUEST))
                     and 'DISABLED') or ''">
<strong> Parent? &nbsp;&nbsp; Backlink </strong>
<br>
<dtml-in "aq_parent.objectValues(spec='ZWiki Page')" sort=id>
<dtml-unless "_.string.find(_.getitem('sequence-item').raw,thispage) == -1">
  <dtml-let thisitem="_.getitem('id')()"
        thisisparent="thisitem in thisparents">
    &nbsp;&nbsp;<dtml-unless thisisparent>&nbsp;&nbsp;</dtml-unless>
       <input type=checkbox name="parents" value="<dtml-var thisitem>"
              <dtml-if "thisitem in thisparents">CHECKED</dtml-if>
              &dtml-maybedisabled;>
    &nbsp;&nbsp;&nbsp;&nbsp;<dtml-if thisisparent>&nbsp;&nbsp;</dtml-if>
<a href="../<dtml-var "_.getitem('id')()" url_quote>">
<dtml-var "_.getitem('id')()"></a><br>
  </dtml-let>
</dtml-unless>
</dtml-in>
</dtml-let>

<p>
<input type="submit" value="Reparent">
<input type="reset" value="Reset Form">
</p>

</form>

<p> <a name="nesting"><a href="../<dtml-var id>"><dtml-var id></a></a> nesting
context in the Wiki folder, including offspring, ancestors, and siblings.
(Branches are abbreviated with '...' elipses after the first time they're
spelled out.)

<dtml-var "context(REQUEST, with_siblings=1)">

<p>
<!-- start of standard_wiki_footer -->

<dtml-let editor="isAllowed('edit', REQUEST=REQUEST)"
      notediting="_.string.find(URL0, 'editform') == -1"
   notcommenting="_.string.find(URL0, 'commentform') == -1"
       commenter="isAllowed('comment', REQUEST=REQUEST)">

  <form method="POST" action="SearchPage">
  <table width="100%" border="0"
         cellspacing="0" cellpadding="5" bgcolor="eeeeee">
    <tr valign="top">
      <td>
        <dtml-if notediting>
          <a href="&dtml-wiki_page_url;/editform"> 
            <dtml-if editor> Edit <dtml-else> View source </dtml-if>
          </a>
        </dtml-if>
        <dtml-if "notcommenting and commenter">
          <dtml-if notediting> or </dtml-if>
            <a href="&dtml-wiki_page_url;/commentform"> Comment on </a>
        </dtml-if>
         <em> <dtml-var id size=30> </em>
        <br>
         <font size="-1">
          Page <a href="&dtml-wiki_page_url;/advancedform">Advanced Actions</a>
          and <a href="&dtml-wiki_page_url;/pagehistory">History</a>
         </font>
        <br>
        Visitor: <em>
        <dtml-var "REQUEST.cookies.get('zwiki_username',
                                   REQUEST.AUTHENTICATED_USER.getUserName())">
        </em>
      </td>
      <td align="right" valign="top">
        <input type="hidden" name="source" value="jump">
        <a href="&dtml-wiki_base_url;/JumpTo">Jump to</a>:
        <input name="expr" type="text" size="20" value="">
      <small>
      <em>
      <br>
      Enter a pagename prefix or search term & press enter.
      <br>See </em><a href="&dtml-wiki_base_url;/SearchPage">SearchPage</a><em>
      for full search,
      </em><a href="&dtml-wiki_base_url;/FrontPage">FrontPage</a><em> for
      orientation.
      </em>
      </small>
      </td>
    </tr>
  </table>
  </form>

  <dtml-if standard_html_footer>
    <dtml-var standard_html_footer>
  <dtml-else>
    </BODY>
    </HTML>
  </dtml-if>
</dtml-let>
''')
#####################################################################
