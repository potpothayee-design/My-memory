# Smart lamp thesis — 1.0 comments vs. 2.0 revision: alignment check

**Checked 2026-10-02.** Compares the adviser's comment rail in **1.0**
(`archive/2026-10-smart-lamp-thesis.md`) against the revised text in **2.0**
(`archive/2026-10-smart-lamp-thesis-v2.md`).

Method: full text of both docs read and compared item by item. Both are journal-style snapshots;
no images were captured in either, so anything figure-related is marked "can't verify."

**Note on "marked as done."** The 1.0 export contains exactly six status entries and no comment
text attached to them: `[r] Marked as resolved`, `[s] Re-opened`, `[t] Marked as resolved`,
`[u] Re-opened` (all anchored to the Chapter 2 heading) and `[w] Marked as resolved`,
`[x] Re-opened` (anchored to the Fishbone heading). The export does not tie those status changes to
individual comment numbers, so this check covers **all 40 items [a]–[an]**.

---

## Verdict

**2.0 aligns with only part of the rail.** Chapter 1's rewrite landed; Chapter 2 partly went
backwards; everything else is untouched.

| Status | Count | Items |
|---|---|---|
| ✅ Fixed and aligned | 4 | [e], [f], [j], [k] |
| 🟡 Half-done / now internally contradictory | 2 | [c], [d] |
| ⚠️ Backwards vs. 1.0 | 4 | [a], [b], [n], [o] |
| ❌ Not addressed | 21 | [g], [h], [i], [l], [p], [q], [z], [aa], [ab], [ac], [ad], [ae], [af], [ag], [ah], [ai]–[an] |
| ❓ Can't verify (figure) | 1 | [v] |
| ℹ️ No action needed (praise / status row) | 8 | [m], [y], [r], [s], [t], [u], [w], [x] |

**The headline problem:** the title now says **"Dual-Mode"** but the body still says **"Hybrid"**
in five places — Theoretical Framework, Statement of the Problem (twice), Specific Objective 6, and
Section 3.2.2.3. Comment [c]'s first item was *"Finalize 'hybrid' versus 'dual-mode'"* — that is not
done; 2.0 is now internally inconsistent.

**The second problem:** the Chapter 2 rewrite of 2.2.6–2.2.9 is **less formal** than the version in
1.0. All four sentences the professor quoted in comment [p] are present in 2.0 (2.2.7 and 2.2.8) and
absent from 1.0's body text.

---

## A. Fixed in 2.0 — genuinely aligned

| # | The professor asked | What 2.0 did |
|---|---|---|
| **[e]** | Restructure the Background into 8 steps: lighting → need for contactless/mobile control → 3-DOF positioning → servo error problem → need for calibration → research gap → solution | Background rewritten and follows the exact sequence. ✅ |
| **[f]** | "The current version becomes highly technical very early. Strengthen the real-world motivation first." | New opening: importance of lighting → physical switches and manual repositioning are inconvenient when hands are occupied → smart lighting. ✅ |
| **[j]** | Drop repeated "might/may"; add the institution as a beneficiary; don't promise untested benefits; handle accessibility carefully | Significance rewritten in concrete future tense; "Faculty and Academic Institutions" added; "rather than making claims regarding accessibility or user experience that are outside the scope of the evaluation." ✅ |
| **[k]** | Suggested beneficiaries: Users, CpE students, Faculty/institutions, Embedded-system & HCI researchers, Future researchers, Smart-lighting developers | All six appear in the same order. ✅ |

## B. Backwards versus 1.0

| # | The professor asked | What 2.0 did |
|---|---|---|
| **[a]** | Fix fragments, commas, capitalization, tense, informal language, apostrophes, plurals, inconsistent terminology; examples: "arms parts," "the users hand," "arduino," "Creates the proper control signals." | Status: ⚠️ **still present, and one is new.** "the arms parts" now appears in 2.2.8; "the users hand" and "Creates the proper control signals, for the servo motors and the LED." remain in 3.1.5; "an arduino-based robotic arm" remains in 2.1.5 / 2.2.10. |
| **[b]** | Future tense for procedures, past tense for cited studies, no first person, define acronyms at first use | ⚠️ **Regressed.** New first-person in 2.2.6 ("We ran an accuracy test"), 2.2.7 ("we have used gesture-controlled devices… we can suggest"). 1.0 had none of this. |
| **[n]** | Uniform academic tone; no long paragraphs; a synthesis per subsection; distinguish accuracy/tracking/trajectory/localization error; don't equate %/degrees/mm; complete citation details | ⚠️ **Regressed.** 2.2.6, 2.2.7 and 2.2.9 now open with **no author-year citation at all** ("This study shows…", "Developed a robotic arm…", "Developed RoboVR…"), and 2.2.8 uses "Alsayaydeh and colleagues in 2025" instead of a citation. |
| **[o]** | "Noticeable decline in academic writing quality beginning around Sections 2.2.6 to 2.2.10" | ⚠️ **Worse.** 2.0's 2.2.6–2.2.9 are the informal passages; 1.0's were rewritten into formal prose with the study data intact. |

**Also lost data.** 1.0's 2.2.6 reported Suryadarma's specifics — 30 repetitive trials, 500 mm travel,
mean positional bias ≈ 0.593 mm, range 0–1.2 mm. 2.0's 2.2.6 dropped them entirely. If 1.0's
versions are yours, they are the better base; 2.0's rewrite should not ship.

## C. Half-done — comment [c] and [d]

Comment [d] (the adviser's final remark) asked for three things: treat the prototype as **dual-mode**;
evaluate the gesture and mobile interfaces for **command reliability and response time**; evaluate
servo calibration through **pre/post-calibration positional error and repeatability**.

| Item | 2.0 |
|---|---|
| Terms: hybrid → dual-mode | 🟡 Title and Background only. "Hybrid" survives in the Theoretical Framework, SOP, Specific Objective 6, 3.2.2.3, and in 2.1.1.1's closing line. |
| Reliability + response time in the research questions | ❌ SOP unchanged — those measures still appear nowhere in the questions. |
| Pre/post-calibration questions | ❌ SOP unchanged. |
| 350° vs. 180° base motion resolved | ❌ Both docs still state 0°–350° with no feasibility explanation. |
| Chapter 3 completed | ❌ Same empty headings as 1.0 (weight, actuators, voltage, camera, functionality testing, calibration, data processing, target error, phone-controller testing). |
| Formulas and performance measures defined | ❌ None added — no MAE, no accuracy formula, no repeatability measure, no recognition-success rate, no response-time definition, no statistical treatment. |
| Torque and power calculations; Raspberry Pi Zero 2 W / MediaPipe / servo feasibility; mode-conflict prevention; source verification | ❌ Nothing added. |
| Definition of Terms completed | ❌ Still only the word "Acronym". |
| Diagrams, mobile-app details, figure quality, ethics/privacy | ❌ No architecture/wiring/flow diagrams, no app details, no ethics or camera-data privacy text. |

---

## D. Full matrix — all 40 items

| # | What the professor asked (short) | Status | Evidence in 2.0 |
|---|---|---|---|
| a | Language quality list + examples | ⚠️ Backwards | Examples still present; "arms parts" now inside 2.2.8 |
| b | Style rules (tense, no first person, acronyms) | ⚠️ Backwards | First person added in 2.2.6, 2.2.7 |
| c | Priority revision checklist, High + Medium | 🟡 Partial | Title → Dual-Mode; everything else open (see §C) |
| d | Final adviser's remark: dual-mode + reliability/response time + pre/post calibration | 🟡 Partial | Title/Background only; measurement design not adopted |
| e | Background progression (8 steps) | ✅ Fixed | Background rewritten in that exact order |
| f | Lead with real-world motivation | ✅ Fixed | Opens with switch/repositioning inconvenience |
| g | SOP issues: Q2/Q3 overlap, Q4 undefined "hybrid mode," missing reliability/response-time questions | ❌ Not addressed | SOP is unchanged, word for word |
| h | Ready-made revised SOP text | ❌ Not addressed | Not adopted anywhere |
| i | Scope corrections: consistent joint terms, scope vs. delimitation, exact gesture count, brightness vs. positioning, LED in functional testing, 350° feasibility | ❌ Not addressed | Scope/Delimitation identical to 1.0 |
| j | Significance suggestions | ✅ Fixed | Concrete claims; accessibility explicitly scoped out |
| k | Six named beneficiaries | ✅ Fixed | All six present |
| l | Definition of Terms: 19 terms listed | ❌ Not addressed | Still "Acronym" only |
| m | Praise: RRL covers the needed areas | ℹ️ No action | — |
| n | RRL major recommendations | ⚠️ Backwards | 2.2.6/2.2.7/2.2.9 now lack citations |
| o | Decline in quality, 2.2.6–2.2.10 | ⚠️ Backwards | Those sections are the informal text now |
| p | Four specific sentences to rewrite | ❌ Not addressed | All four present in 2.0 (2.2.7, 2.2.8); none in 1.0's body |
| q | Standard structure per study (author/year → purpose → system → results → relevance → gap) | ❌ Not addressed | 2.2.6, 2.2.7, 2.2.9 start without author/year |
| r | *Marked as resolved* (status entry) | ℹ️ Status | Not tied to a comment number in the export |
| s | *Re-opened* (status entry) | ℹ️ Status | Same |
| t | *Marked as resolved* (status entry) | ℹ️ Status | Same |
| u | *Re-opened* (status entry) | ℹ️ Status | Same |
| v | Fishbone: root causes not confirmed until prototype data; regenerate the figure legibly | ❓ Can't verify | Text unchanged; figure not captured in the text export. See §E — the Validation column was partly blanked, which may be the response |
| w | *Marked as resolved* (status entry) | ℹ️ Status | Same |
| x | *Re-opened* (status entry) | ℹ️ Status | Same |
| y | Praise: validation tables give good traceability | ℹ️ No action | But see §E — the Validation column is now inconsistent |
| z | Chapter 3 incomplete (lists 9 empty headings) | ❌ Not addressed | Identical empty headings |
| aa | 14 additions required before approval (architecture, block/wiring diagrams, BOM, trial plan, formulas, statistical treatment, safety, acceptance criteria, ethics…) | ❌ Not addressed | None appear |
| ab | Per-component materials incl. screws; bearings; cable routing; mechanical stops | ❌ Not addressed | 3.1.1 unchanged |
| ac | Full servo documentation + how 350° is achievable | ❌ Not addressed | 3.1.4 Actuators still empty |
| ad | 11 technical clarifications (Pi↔Arduino protocol, command format, mode logic, conflict prevention, voltage, ground, e-stop, startup, invalid commands, separate servo supply, BT takeover) | ❌ Not addressed | Only the one-line "only one active at a time" in Scope |
| ae | ML contradiction: a pretrained model is still ML | ❌ Not addressed | 2.1.1.1 still says "without machine learning"; 3.2.1.2 still loads a `.task` model |
| af | Recommended wording for inference-only use | ❌ Not addressed | Not used |
| ag | 11 MediaPipe details (model, version, license, threshold, FPS, debounce, unknown gestures, trials, definitions) | ❌ Not addressed | None appear |
| ah | Privacy: are images stored? consent, retention, deletion | ❌ Not addressed | No privacy text anywhere |
| ai | MAE, signed error, percentage-error caveat | ❌ Not addressed | Only the absolute-error line from 1.0 |
| aj | Positional-accuracy formula, or justify reporting degrees | ❌ Not addressed | — |
| ak | Repeatability measures, ≥3 trials per condition | ❌ Not addressed | — |
| al | Recognition success rate formula; record correct/incorrect/failed separately | ❌ Not addressed | — |
| am | Response time: define start and end | ❌ Not addressed | — |
| an | Statistical treatment: hypotheses, α, assumptions, trial count, unit of analysis | ❌ Not addressed | — |

---

## E. Inconsistencies inside 2.0 (worth fixing even apart from the rail)

1. **Dual-mode vs. hybrid** — title and Background say dual-mode; Theoretical Framework, SOP,
   Specific Objective 6, and 3.2.2.3 say hybrid.
2. **Validation column half-cleared.** In 2.0's Root Cause Validation Summary, rows 1–4 and 7 now
   read `-`, but row 5 still says `VALID` and row 6 `INVALID`; the Solution Validation Summary is
   `-` throughout. Meanwhile the prose in 2.3.2.1–2.3.2.7 still asserts "valid direct root cause" /
   "valid indirect factor." If the intent was comment [v] ("not confirmed until prototype data"),
   blank all of it and soften the prose; if not, restore the judgments. Right now it reads as an
   accident.
3. **Citation style broken in Chapter 2** — 2.2.6, 2.2.7, 2.2.9 have no author-year at all, which
   contradicts comment [n] and makes the bibliography (whenever it is written) harder to match.
4. **Numbering gap** — Chapter 3 jumps from 3.2 to 3.4 in both versions; 3.3 is missing.
5. **"Figure 2.X" vs. "Figure 2.5"** for the same fishbone diagram (both versions).

## F. What I could not check

- **Any figure.** Neither export carries images: the fishbone diagram, the IPO diagram, the gesture
  table illustrations, the SolidWorks shots, and the new figures [aa] asks for. Whether the fishbone
  was regenerated per [v] cannot be judged from text.
- **The bibliography.** Neither document contains one — so [n]'s "verify all citations appear" and
  "check credibility of 2025/2026 sources" are pending by definition.
- **Which comments are actually marked as done.** See the note at the top — the export gives six
  status entries without linking them to comment numbers.

## G. Suggested order of attack

1. **Settle the term.** Replace "hybrid" with "dual-mode" in the five remaining places, or state
   explicitly that hybrid = dual-mode is used deliberately. (Comment [c], item 1.)
2. **Paste in the adviser's SOP from [h] verbatim** — it already answers [c], [d] and [g] at once.
3. **Restore 2.2.6–2.2.9 from 1.0** (they are formal and keep the data), then add the missing
   author-year citations and per-study structure from [q]. Do not ship 2.0's versions.
4. **Decide the Validation column deliberately** and make prose and table agree. ([v], [y])
5. **Chapter 3 block** — [z], [aa], [ab], [ac], [ad] plus the formula/statistics set [ai]–[an] is
   where the approval risk actually sits; none of it has been started in either version.

---

*Checked 2026-10-02 against 1.0 and 2.0 as captured on the same date. If either doc changes, re-run
this check — the snapshots in `archive/` are frozen at their capture date.*
