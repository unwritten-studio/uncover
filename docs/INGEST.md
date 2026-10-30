# Ingesting new versions

## The situation

Bernd delivers a new version of his manuscript as a PDF every one to two weeks. He works in his own writing tool and will keep doing so; working in this repository is not part of his process and is not expected to become so.

So the repository adapts to him, not the other way round. Absorbing a new version must be routine: one command, a readable report, a small number of decisions.

## What can be automated, and what cannot

**Fully mechanical (no model involved):** extracting the text, cleaning it up, splitting it into passages, recognising which passages are unchanged, moved, edited, new or removed, and listing which cards and scenes are affected.

**Needs judgment:** whether a change matters for the novel. A corrected typo does not. A new anecdote might become a scene. That decision is made per change, but only for the changes, never for the whole book again.

The cost of a new version therefore scales with *how much Bernd changed*, not with the size of the book.

## How it works

```
new PDF
  │
  ▼
1. extract      text out of the PDF, page furniture removed
                (page numbers, running heads, hyphenation)
  │
  ▼
2. segment      split into passages, each with a stable ID
  │
  ▼
3. match        compare with the previous version:
                identical       → same ID
                slightly edited → same ID, marked "edited"
                moved           → same ID, new position
                no match        → new ID, marked "new"
                gone            → marked "removed"
  │
  ▼
4. impact       edited/removed passages → the cards that cite them
                → the scenes that use those cards
  │
  ▼
5. report       one Markdown report per version:
                what changed, what it touches, what needs a decision
```

Passage IDs survive reordering and light editing because they are matched by content similarity, not by position. That matters: Bernd regularly restructures and renames chapters.

## Where things live

```
sources/bernd/2026-10-28/
  manuscript.md      extracted, cleaned text
  passages.jsonl     one passage per line, with stable ID
  manifest.json      date, checksum, page and word count
sources/reports/
  2026-10-28.md      change report for this version
```

The PDFs themselves are attached to a GitHub release per version (`source-YYYY-MM-DD`) rather than committed, so the repository stays small while every original remains retrievable. The extracted text is in git, which means the plain `git diff` between two versions is readable as well.

## After the report

For every flagged change, one of three outcomes, recorded in the report:

- **ignore** — no effect on the novel
- **update card** — the card is corrected; scenes using it are re-checked
- **rework scene** — a new brief goes to the local model

## Limits

- Very large restructurings (half the book rewritten) will produce a long report. The process still works; it is just more decisions.
- PDF extraction depends on the export. Should the export format change, the extract step may need adjusting. This shows up immediately in the report as an implausible number of changes.
