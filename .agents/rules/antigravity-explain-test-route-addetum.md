---
trigger: always_on
---

---
trigger: always_on
---

# ANTIGRAVITY_EXPLAIN_TEST_ROUTE_ADDENDUM.md

**Add this as a new file `.agents/rules/explain-test-route.md` in the repo**
(Antigravity auto-loads everything in `.agents/rules/`, same as playbook.md).
This patches the gap where Antigravity builds things silently without
explaining them — it strengthens PLAYBOOK.md §3, doesn't replace it.

---

## Why this file exists
Not every teammate on this project is a strong coder. If Antigravity just
writes code and moves on, the person who asked for it can't verify it works,
can't explain it to a judge, and can't catch a bug before it becomes a demo
crash. From now on, **every response from Antigravity that changes code must
end with three things, every time — not just at full milestone completion:**

## Rule 1 — Plain-language "what I just did" (every response, not just milestones)
After any code change, however small, Antigravity ends its response with a
short section:
```
### What I just built (plain language)
[3-5 sentences, no jargon, explaining what changed and why, as if to someone
who doesn't read code. If a term must be used (e.g. "vectorized", "Pydantic
model"), define it in one clause the first time.]
```
This is not optional and not just for "big" changes — a single function is
still worth one paragraph. Skipping this because "it's a small change" is not
acceptable; small changes compound into a codebase nobody but Antigravity understands.

## Rule 2 — Manual test steps (every response, not just milestones)
Immediately after the plain-language summary:
```
### How to check this yourself, manually
1. [Exact command to run, or exact URL to open, or exact curl/Postman call]
2. [What you should see if it worked — the literal expected output/response]
3. [What it looks like if it's broken, so you don't mistake a failure for success]
```
This must be concrete enough that someone who has never seen the code can
follow it — no "run the test suite and check it passes" without saying which
command, no "check the dashboard" without saying what URL and what to look for.

## Rule 3 — Milestone completion: report + literal copy-paste block
When a full milestone (a complete layer, not just one function) is reached,
in addition to Rules 1 and 2, Antigravity must:
1. Generate the full milestone report per `milestone-report-template.md`
   (including its new "How to Test This Manually" section — see the updated
   template), saved to `/reports/`.
2. **Print the routing line, AND immediately below it, a ready-to-copy block**
   — not just a pointer to the file. The person should never have to go dig
   through `/reports/` and reformat something themselves. Format exactly:

```
ROUTE THIS REPORT → [tool(s)] → ask: "[specific question]"

────────────── COPY EVERYTHING BELOW THIS LINE ──────────────
[Paste-ready block: 1-paragraph plain-language summary of what was built,
the specific review question from the ROUTE line above, and the key numbers/
test results from the milestone report — self-contained, so the receiving
tool doesn't need any other file to give a useful answer]
────────────────────────────────────────────────────────────
```

3. Tell the person explicitly, in the response, which tool that block goes
   to: **"Paste the block above into ChatGPT"** (Alpha) or **"Paste the block
   above into your Gemini Gem"** (Beta/Gamma) — matching whichever of
   ALPHA.md/BETA.md/GAMMA.md's tool assignment applies — and separately note
   if it should also go to Claude or Kimi per the routing table.

## Rule 4 — If something fails or is uncertain, say so plainly, immediately
Never silently work around a failing test, an ambiguous schema field, or a
missing data source. Stop, state exactly what's blocking, in plain language,
and ask before proceeding — this was already true per playbook.md §3, this
addendum just makes explicit that it applies to every response, not just full
milestones.

---

## One-time prompt to adopt this protocol retroactively
Paste this into Antigravity once, in your next session, regardless of which
layer you're on:
```
A new rule file .agents/rules/explain-test-route.md now exists — read it.
From this point forward, apply all 4 of its rules to every response that
changes code, including for work already in progress on this branch. If any
previously-completed function or layer on this branch doesn't yet have a
plain-language explanation and manual test steps, generate them retroactively
now before continuing new work, so the person picking this up isn't lost.
```
but dont forget to also give detailed report of what is built for each time***

And also tell when you're ready for a next prompt 