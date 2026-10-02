# BRAIN.md

<!-- HOT MEMORY — always loaded. Hard cap ~150 lines.
     When it outgrows the cap, demote detail to archive/ and leave a row in the Archive Index. -->

**Last updated:** 2026-10-02 · **Owner:** hycee · **Location:** Angeles City, Philippines
**Timezone:** Asia/Singapore (UTC+8) · **Language:** English

---

## 0. Protocol — for the assistant reading this

You are picking up where the last assistant left off. Don't start from zero.

| | Rule |
|---|---|
| **READ** | Fetch this file at session start. It is the entire hot context. |
| **COLD** | Do NOT fetch `archive/` unless the topic matches an Archive Index row below. One match → one fetch. |
| **WRITE** | Only when I say **"update my brain"**. With repo access granted this session → commit and push the new file yourself. Without it → print a complete replacement in one copy-paste block. Never auto-commit between sessions, never ask me for a token. |
| **DON'T GUESS** | If it isn't in this file, say "not in memory." An honest gap beats a confident invention. |
| **CONFLICT** | If this file contradicts something I say in chat, trust the chat and flag the mismatch so it gets fixed. |

## 1. How to answer me

- **Direct answer first. Detail after.** No filler intros, no restating my question.
- **Name the catch.** Every recommendation gets its tradeoff, not just the upside.
- **Say "I can't verify this"** when you can't. That beats a confident guess.
- **Tables for comparisons.** Not prose lists.
- **Verify with a tool when verification is cheap.** Don't tell me what you could have checked.

## 2. Who I am

- Call me **hycee**.
- Based in **Angeles City, Philippines** — UTC+8. My "today" is Asia/Singapore time.
- Writes in English.
- **Technical level:** comfortable editing files and running simple commands. **Self-hosting —
  Docker, VPS, cron — is explicitly unfamiliar.** Don't route answers through self-hosting, and if
  there's no way around it, flag that up front rather than burying it in step 4 of a guide.

## 3. What I'm working on

**Main project: a portable memory system** — so any AI assistant can pick up where the last one
left off. A public GitHub repo holds this file; I paste a load-line at the start of a chat; at the
end I say "update my brain" and it prints a new version for me to paste-commit.

- Repo: `github.com/potpothayee-design/My-memory` (public)
- Load-line URL: `https://raw.githubusercontent.com/potpothayee-design/My-memory/main/BRAIN.md`

**What I use AI for, roughly in order:**

| Use | Notes |
|---|---|
| **Websites** | Heaviest interest — mostly **HTML and CSS**. Don't assume a build toolchain, Node, or a framework unless asked. |
| **Research** | Gathering, comparing, and summarising |
| **Building apps** | Tools and projects that ship |
| **Documents** | Writing, editing, long-form |
| **Skill expansion** | Day-to-day exploration of how to get better at this |

**Status (2026-10-02):** this file was rebuilt from my own written summary plus my answers. The
identity and preferences are mine and confirmed. Treat §4 as settled unless I say otherwise.

## 4. Decisions & rationale — don't relitigate these

These were deliberate. If you're about to suggest one of the rejected options, read Why first.

| Decision | Why | Rejected alternative |
|---|---|---|
| Memory is **read over a plain public URL** | Any assistant can fetch a raw GitHub URL with zero credentials and zero setup | API keys, MCP servers, proprietary sync |
| **WRITE is manual** — AI prints, I commit | I'm not handing a push token to a platform that may use prompts as training data. The ~15-second commit is a deliberate tradeoff, not a gap to fix | Auto-commit / write-back |
| The repo is **PUBLIC** | It has to be, for credential-free reads | Nothing sensitive goes in it — no keys, no passwords, no client data |
| **HOT/COLD split** | `BRAIN.md` loads every session, so it must stay small. Detail lives in `archive/` and is fetched only on topic match | One giant file that bloats every session |
| **Plain markdown over a URL** | Works with any assistant, indefinitely. No vendor lock-in | Any single vendor's memory feature |

## 5. Working preferences

- **Genuinely free tools only.** Not trials. Not "free tier" credits that evaporate in a day.
- **If something has limits, say so up front** — before I invest time in it.
- Assume **no self-hosting** (see §2). Prefer things that run in a browser or as a single local file.

## 6. Archive Index

Cold storage. Fetch a file **only** when the topic matches. Don't preload these.

| File | Covers | Fetch when |
|---|---|---|
| `archive/2026-10-tools.md` | Tool picks, free-tier limits, what I actually run | I ask about tools, costs, or what to run something on |
| `archive/README.md` | How the cold layer works (meta, not memory) | Only if editing the archive structure |

## 7. Open Questions

Still unrecorded. Fill these in on the next "update my brain".

| # | Question | Why it matters |
|---|---|---|
| 1 | Which websites or apps are actually in flight right now? | Turns generic help into specific help |
| 2 | Which tools am I actually using day to day? | `archive/2026-10-tools.md` is still a skeleton |

---

*Protocol: read this file → answer → on "update my brain", emit a full replacement.*
