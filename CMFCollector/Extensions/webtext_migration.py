"""Convert collector issue instances transcripts to WebTextDocument.

This is only necessary if you used a pre-1.0 version of the collector.  If you
did, create an external method in your portal root:

  o id: collector_webtext_migration

  o title (optional): Upgrade collector issues (temporary)

  o module name: CMFCollector.webtext_migration.py

  o function name: collector_webtext_migration

For each collector, visit the visit the URL constructed of the URL for the
collector plus '/collector_webtext_migration'.  This will run the method on
the collector, producing a (sparse) page reporting the changes, or that no
changes were necessary.

The process may take a while, if your site catalogs a lot of objects - the
converted issues are (necessarily) reindexed, internally and in the site
catalog.

You can delete the external method once you've upgraded your preexisting
issues - it won't be needed after that."""

MIGRATE_ATTRIBUTES = ['effective_date',
                      'expiration_date',
                      '_isDiscussable',
                      '_stx_level',     # even though we don't use it
                      '_last_safety_belt_editor',
                      '_last_safety_belt',
                      '_safety_belt',
                      ]

from Products.CMFCollector.WebTextDocument import WebTextDocument
from Products.CMFCollector.CollectorIssue import RULE
import re

tidypre = re.compile("\n</?pre collector:deleteme>\n").sub
tidyleadspace = re.compile("\n ([^ ])").sub

def collector_webtext_migration(self):
    """Migrate old CMF "Document" based transcripts to "WebTextDocument"."""
    total_changed = 0
    issues = self.objectValues(spec="CMF Collector Issue")
    for issue in issues:
        transcript = issue.get_transcript()
        was_p_mtime = transcript._p_mtime
        was_creation_date = transcript.creation_date
        changed = 0
        if transcript.meta_type != "WebText Document":
            changed = 1
            webtext = WebTextDocument(transcript.id,
                                      title=transcript.title,
                                      description=transcript.description,
                                      text=transcript.text)
            for attr in MIGRATE_ATTRIBUTES:
                if hasattr(transcript, attr):
                    setattr(webtext, attr, getattr(transcript, attr))
            issue._delObject(transcript.id)
            issue._setObject(webtext.id, webtext)
            transcript = getattr(issue, webtext.id)
        if changed or transcript.text_format != 'webtext':
            total_changed += 1
            transcript.text_format = 'webtext'
            transcript.cooked_text = ''
            text = tidypre('\n', transcript.text)
            text = tidyleadspace('\n\\1', transcript.text)
            text = text.replace('\n<hr>\n', '\n' + RULE + '\n')
            
            transcript.text = text      # Ditch garbage
            transcript.edit('webtext', text)      # Cook the text.
            transcript._p_mtime = was_p_mtime
            transcript.creation_date = was_creation_date
            transcript.meta_type = "Collector Issue Transcript"
    if total_changed:
        self.reinstate_catalog()
        return ("Converted %d of %d issues, and reinstated catalog"
                % (total_changed, len(issues)))
    else:
        return ("No changes, all issues are current.")
