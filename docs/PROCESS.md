# Process

The method follows [Buchleim](https://buchleim.unwritten.studio) — ten steps, from the shoebox of raw material to the bound book. Its core rule applies throughout: **nothing scales before it has been tested.**

## Who does what

| Role | Does | Does not |
|---|---|---|
| **Claude** | Analysis across the whole book, all structural and stylistic decisions, writing briefs, reviewing output, all code, all repository work | Bulk text production |
| **Local model** | Text work against a precise brief: breaking passages into cards, drafting scenes, revision passes | Decisions, structure, tools, repository access |
| **Humans** | Reading and judging: does it carry? Approving the sample chapter and each stage | — |

The local model sees only one excerpt plus one brief at a time. It never sees the whole book and never needs to: the overview is held by Claude, in the files in `architecture/`. Every brief sent to the local model is stored in `briefs/`, so every piece of text can be traced to the instruction that produced it and regenerated if the brief changes.

## The ten steps applied to Uncover

| # | Buchleim | In this project | Who |
|---|---|---|---|
| 01 | Secure the sources | Each version of Bernd's PDF extracted into `sources/`, never edited | Claude (script) |
| 02 | Inventory | What is in the manuscript; what changed since the last version | Claude (script) |
| 03 | Expose the inner order | **The mixer:** every passage broken into cards (scene, person, fact, quote, anecdote, motif), each card pointing back to its source passage | Local model, Claude reviews |
| 03 | | Merging the cards: who appears where, which threads and motifs run through | Claude |
| 04 | Model the voice | A compact style model for the novel, including explicit exclusions (no copied phrasing, no pastiche) | Claude |
| 05 | Choose the medium | Novel, printed book | decided |
| 06 | Build the structure | The narrative layers, how they mirror each other, a scene plan with a brief per scene | Claude |
| 07 | Derive the form | Typography and layout for the printed book | later |
| 08 | Prototype | **One sample chapter**, drafted by the local model from its briefs, read by humans. Go / no-go for everything after. | Local model, humans decide |
| 09 | Calibrate | Sharpen the style model and briefs, not the output text by hand | Claude |
| 10 | Produce | Scene by scene, followed by revision passes against checklists; build to PDF | Local model, Claude reviews |

## Working rules

- **Sources are read-only.** Nothing in `sources/` is ever edited by hand or by a model.
- **Fix the brief, not the text.** If output is weak, the brief or the style model is wrong. Fixes go there, then the text is regenerated.
- **Traceability.** Scene → cards → source passages. If it cannot be traced, it does not go in.
- **Small steps, reviewed.** Every stage lands as a pull request.
