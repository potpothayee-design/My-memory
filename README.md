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

| Where you are | What lands |
|---|---|
| An assistant with repo access (Arena, or any agent you've connected GitHub to) | It commits and pushes the new `BRAIN.md` directly |
| Any other assistant | It prints a complete replacement in one copy-paste block; you commit it |

Print-and-paste is the baseline — it works with every assistant that can produce text. The push
path only applies in sessions where repo access was explicitly granted.

## File map

| File | Layer | Loaded | Contains |
|---|---|---|---|
| `BRAIN.md` | HOT | Every session | Identity, preferences, active projects, decisions, archive index |
| `archive/*.md` | COLD | Only on topic match | Detail too long for the hot file |
| `archive/README.md` | meta | Rarely | Rules for the cold layer |

## Rules

1. **The repo is public — nothing sensitive goes in it.** No keys, no tokens, no passwords, no client data.
2. **`BRAIN.md` stays under ~150 lines.** When it grows, detail gets demoted to `archive/` and leaves a one-line index row behind.
3. **AI writes only when you've authorized it.** With repo access granted, the assistant commits. Without it, it prints and you commit. Nothing is ever auto-committed between sessions.

## Why it's shaped this way

| Choice | Reason | Tradeoff |
|---|---|---|
| Read over a plain public URL | Any assistant can fetch it with zero credentials | Anyone can read it — so nothing private ever goes in |
| Write works two ways | Print-and-paste works with every assistant; push works when you've granted repo access | In a push-capable session the assistant holds a repo-scoped token |
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
