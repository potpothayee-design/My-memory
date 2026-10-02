# My Memory

A portable memory system: **one small markdown file over a public URL**, so any AI assistant can
pick up where the last one left off.

No app. No account. No API key. No vendor lock-in.

## The load-line

Paste this at the start of a chat:

```
Load my memory: https://raw.githubusercontent.com/potpothayee-design/My-memory/main/BRAIN.md
Fetch that URL, read it, then follow the protocol inside it. Don't fetch anything in
archive/ unless the topic clearly matches an index entry.
```

That is the entire read path. Any assistant that can fetch a URL can load this. Nothing else
required — no credentials, no install, no account.

**One repo, one file.** There is no second repo and no separate `brain` repo to keep in sync.
The brain *is* this repo, and `BRAIN.md` at its root is the hot file.

**Why the account name is in that URL.** The first segment of the load-line is the GitHub
*account* that owns this repo — not a second repo. A raw URL is always `account/repo/branch/file`;
remove the account and it 404s (verified). So the load-line above is the **only** place the full
URL appears. Everything else in this project just says "this repo."

## The write path

At the end of a session, say: **"update my brain."**

Nothing to paste. The assistant writes the updated file and commits it.

Commits land on the assistant's branch; merging to `main` is the owner's click.

### Two directions

| Direction | What happens |
|---|---|
| **You tell it** | You say what changed — a new project, a dropped tool, a corrected preference. It gets written in. |
| **It mines the session** | In a long chat, the assistant re-reads the whole conversation and pulls out what's durable on its own. Preferences you revealed in passing, decisions you made, corrections you gave it. You don't have to remember what was worth keeping. |

Both fire on the same phrase. A short chat mostly takes the first path; a long one takes both.

**What counts as durable:** anything that changes how the assistant answers you next month. Not
today's task, not a one-off question, not a replay of what just happened. Detail too long for the
hot file gets demoted to `archive/`.

**It lists what it mined** before committing, so you can correct it. Wrong memory is worse than no
memory.

### Nothing is captured automatically

There's no background recorder. Nothing is saved while you work — the mining above only happens
when you say the phrase.

**And it only sees the session it's in.** A chat in another tool, or an earlier conversation that's
no longer in context, isn't reachable. If it mattered, it's either already in this file or you have
to say it again.

That's the point: you decide what's true about you, not a vendor's inference engine. The cost is
that the brain only knows what got written down.

### When it goes stale

A memory file you stop feeding is **worse than no memory file** — an assistant reading it will
state outdated facts confidently.

| Signal | What to do |
|---|---|
| `Last updated` over ~2 months old | The protocol tells the assistant to flag it before answering |
| Projects or tools changed | Update — the file is now wrong, not merely old |
| A decision in §4 changed | Update immediately; those rows exist to stop re-litigation |
| A session changed how you work | Say "update my brain" before you close the tab, or it's lost |

**Cadence:** once every few sessions, not every session. Batch it — constant updates cost a merge
click each time and produce a file nobody reads.

## File map

| File | Layer | Loaded | Contains |
|---|---|---|---|
| `BRAIN.md` | HOT | Every session | Identity, preferences, active projects, decisions, archive index |
| `archive/*.md` | COLD | Only on topic match | Detail too long for the hot file |
| `archive/README.md` | meta | Rarely | Rules for the cold layer |

## Rules

1. **The repo is public — nothing sensitive goes in it.** No keys, no tokens, no passwords, no client data.
2. **`BRAIN.md` stays under ~150 lines.** When it grows, detail gets demoted to `archive/` and leaves a one-line index row behind.
3. **Assistants commit; the owner merges.** An authorized session writes and commits directly. Nothing reaches `main` without the owner's merge.

## Why it's shaped this way

| Choice | Reason | Tradeoff |
|---|---|---|
| Read over a plain public URL | Any assistant can fetch it with zero credentials | Anyone can read it — so nothing private ever goes in |
| AI does the commits | The assistant is the one writing, so it's the one committing — no paste step | The owner still approves what reaches `main` |
| Public repo | Required for credential-free reads | No secrets, ever |
| HOT/COLD split | Keeps every session from loading the whole history | The assistant must judge when to open the archive |
| Plain markdown | Works with any assistant, indefinitely | No search, no sync, no automation |

## Limits

- **A fetch is not always available.** A tool-using assistant can read a raw GitHub URL. Some code
  execution sandboxes cannot reach `raw.githubusercontent.com` at all — verified: a plain `curl` in
  one such sandbox fails entirely, while the assistant's own fetch tool succeeds. So "any AI can
  load this" is *almost* true, not universally true.
- **Memory only updates when you say so.** Nothing is captured automatically between sessions.
- **One file, one owner.** No merge logic. If two chats update the brain, you reconcile by hand.
