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

## The write path

At the end of a session, say: **"update my brain."**

The assistant prints a complete replacement file in a copy-paste block. You commit it.

That friction is deliberate — see the table below.

## File map

| File | Layer | Loaded | Contains |
|---|---|---|---|
| `BRAIN.md` | HOT | Every session | Identity, preferences, active projects, decisions, archive index |
| `archive/*.md` | COLD | Only on topic match | Detail too long for the hot file |
| `archive/README.md` | meta | Rarely | Rules for the cold layer |

## Rules

1. **The repo is public — nothing sensitive goes in it.** No keys, no tokens, no passwords, no client data.
2. **`BRAIN.md` stays under ~150 lines.** When it grows, detail gets demoted to `archive/` and leaves a one-line index row behind.
3. **No AI writes to this repo.** Assistants print; the human commits.

## Why it's shaped this way

| Choice | Reason | Tradeoff |
|---|---|---|
| Read over a plain public URL | Any assistant can fetch it with zero credentials | Anyone can read it — so nothing private ever goes in |
| Write is manual | No push token is handed to a platform that may train on prompts | ~15 seconds of copy-paste per update |
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
