# Uncover

**Worte werden Welten.** A novel built from the raw material of [unwritten](https://unwritten.studio/).

---

## What this is

Since 2022, unwritten has been making stories walkable — books that talk back, companions built from knowledge, conversations with literature. Bernd has been chronicling that journey as a non-fiction manuscript, *Das begehbare Buch 2.0*.

This repository turns that manuscript into something else entirely: **a novel.**

Not a cleaned-up edition. Not a chapter-by-chapter rewrite. The manuscript goes through the mixer — taken apart into its smallest pieces: scenes, people, facts, quotes, anecdotes, motifs. From that card box, a new book is built: one that weaves its story across several narrative layers and is genuinely gripping to read.

The inspiration is Wolf Haas' *Wackelkontakt* — not to copy it, but as proof of what becomes possible when you master your craft and can braid a story across levels. See [`docs/GOAL.md`](docs/GOAL.md).

## How it works

The method is [Buchleim](https://buchleim.unwritten.studio): first understand what is there, then decide what becomes of it. Ten steps, from securing the sources to binding the book.

Work is split by kind:

- **Thinking, structure, decisions, code, repository** — Claude.
- **Text work** (breaking down, drafting, revising against precise briefs) — a local model.
- **Judgment on what reads well** — humans. Nothing scales before a sample chapter has been read and approved.

Details: [`docs/PROCESS.md`](docs/PROCESS.md).

## A moving source

Bernd keeps writing. A new version of the manuscript arrives as a PDF every one to two weeks. That is not a problem to be solved, it is the working condition. Every new version is ingested the same way: extracted, compared against the previous one, and only what actually changed flows into the card box and, where it matters, into the novel.

Details: [`docs/INGEST.md`](docs/INGEST.md).

## Status

Fresh start on 2026-10-30. Everything earlier (the open non-fiction draft and the editing dashboard) was cleared from this branch of work; it remains available in the git history up to commit `2663c97`.

What happens next and what is done: [`ROADMAP.md`](ROADMAP.md).

## Layout (planned)

```
sources/        Bernd's versions, extracted, never edited
zettelkasten/   the cards: the manuscript taken apart
architecture/   style model, narrative layers, scene plan
briefs/         the exact tasks given to the local model
novel/          the novel itself
tools/          ingest and build scripts
docs/           goal, process, ingest design
```

## Team

[unwritten](https://unwritten.studio/) — Worte werden Welten. Contact: post@unwritten.studio
