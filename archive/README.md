# archive/ — the cold layer

Detail that used to live in `BRAIN.md` and got demoted here, so the hot file stays under ~150 lines.

## Rules

- **Nothing here is loaded by default.** The assistant fetches at most one file, only when the
  topic matches a row in the Archive Index in `BRAIN.md`.
- **Every file here needs an index row.** A file with no row is invisible — it will never be
  fetched. Add the row in the same commit as the file.
- **The public-repo rule still applies.** No keys, no passwords, no client data.

## When to demote something out of BRAIN.md

| Signal | Action |
|---|---|
| `BRAIN.md` passes ~150 lines | Demote the least-frequently-needed section |
| A topic needs more than ~15 lines | Give it its own file |
| A fact is stable and rarely relevant | Give it a dated file |
| A fact changes every session | Don't store it at all |

## Naming

`YYYY-MM-<topic>.md` — e.g. `2026-10-tools.md`. The date is when the file was **created**, not
when it was last useful. Don't rename on update; edit in place and bump the `Last updated` line
inside the file.

## Index row format

Add this to the Archive Index table in `BRAIN.md`:

| File | Covers | Fetch when |
|---|---|---|
| `archive/YYYY-MM-topic.md` | one-line scope | the specific trigger condition |

The **Fetch when** column is the important one. Write it as a condition an assistant can actually
test against a question — "I ask about tools, costs, or what to run something on" — not a vague
topic word like "tools".
