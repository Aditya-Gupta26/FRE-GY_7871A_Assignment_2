# Step 1: Understanding the Assignment

**No code in this step.** This was pure reading, research, and planning — but it shaped every decision that came after, so it belongs first in the story.

## What we started with

You gave two things: the assignment PDF ("Evaluating the Impact of FOMC Communications on Asset Prices") and a link to a prior conversation where you'd asked Claude some background questions about how the Fed works — what the FOMC does, how rate decisions transmit through the economy, and how QE works. That transcript turned out to contain no assignment-specific decisions, just general Fed-mechanics education, so it didn't constrain our approach — it just meant you understood the *economics* going in, which was good context but not a technical starting point.

## The first real problem: this assignment is set in a future we don't automatically know about

The assignment's premise is "Kevin Warsh is now Chair of the Federal Reserve." That's not a hypothetical for a course exercise — as of the assignment's due date (September 2026), it's simply what happened. But an AI model's training data has a cutoff, and this event postdates it. Treating it as fiction, or guessing at a plausible-sounding timeline, would have poisoned everything downstream: wrong dates for Warsh's tenure, wrong meeting count, wrong forecast target.

So before writing a single line of code, we used web search to establish the real facts:

- Jerome Powell's term as Chair ended **May 15, 2026** (he continued as "chair pro tempore" briefly, then remains a Governor)
- Kevin Warsh was confirmed by the Senate **May 13, 2026** and sworn in as Chair **May 22, 2026**
- Warsh's **first FOMC meeting as Chair was June 16–17, 2026**
- His second was **July 28–29, 2026**
- The meeting we're forecasting is **September 15–16, 2026**
- Today (per the system clock) was **September 12, 2026** — meaning the assignment's own due date (Sept 15, midnight) arrives *before* the forecasted meeting's decision is even announced (Sept 16). That's an important, freeing fact: the forecast can't be checked against a known answer even in principle, so it's a genuine test of the method, not something to reverse-engineer.

**Why this mattered:** every later step depends on knowing exactly when the "Powell era" ends and the "Warsh era" begins. Get that boundary wrong, and every table, figure, and regression downstream misattributes documents to the wrong chair.

## Building the first plan

With those facts in hand, we wrote a first draft of `PLAN.md` — a single planning document (not code) laying out:

- A restatement of the task in plain terms
- An exhaustive requirements checklist pulled line-by-line from the assignment rubric (so nothing could get silently dropped later)
- A step-by-step approach for each phase of the work, each with a stated rationale
- A list of open questions that only you could answer (did you have the three assigned readings? what GitHub repo? did you have a FRED API key? how much time did we actually have?)

**Why a plan document first, rather than just starting to code:** you explicitly asked for a collaborative, step-by-step process rather than a single unsupervised pass — so the plan was the artifact that let you see and correct the approach *before* hours went into implementing it. It also became the running record of *why* we made each methodological choice, which is exactly what you're reading an expanded version of right now.

## Result

- `PLAN.md` v1 existed, with a clearly flagged critical constraint: **we had roughly 3 days**, not weeks, which shaped every scope decision from that point on (e.g., "3 tone methods, not 5"; "statements-only as the primary regression corpus, pooled-everything as an extension" rather than trying to do everything at maximum rigor).
- Five concrete open items were identified for you to resolve: the three readings, the GitHub repo, a FRED API key, a time-budget confirmation, and local Python setup.

**Next:** [Step 2 — Reading the Research Papers](02-reading-the-research-papers.md), where you sent the three PDFs and the plan changed substantially once we could see the actual methodology instead of guessing at it.
