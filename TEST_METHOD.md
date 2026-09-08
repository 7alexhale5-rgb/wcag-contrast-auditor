# TEST_METHOD.md

Written before any gate below existed. The commit that carries this file is the
freeze; the date in this file is not the proof, the commit timestamp is. This file
is not edited after that commit. Anything that turns out wrong is logged with a
date in `receipts/DEVIATIONS.md`, never corrected here.

## What is being tested

A drop-in folder (`auditor/`) that audits colour pairs against WCAG 2.1 success
criteria 1.4.3, 1.4.11 and 1.4.6, with the number coming from code, never from a
model.

The claim: a person who has never seen this repo can clone it, run one command,
and watch every gate pass, then edit one planted citation and watch the gate name
it and fail. A person with no context can drop `auditor/` into a Claude project,
hand it a colour pair, and get back PASS or FAIL with a criterion number, a
measured ratio against a required ratio, and a file in `reference/` they can open.

The claim is false if: a finding cites a provision that is not in `reference/`;
a quoted requirement is not verbatim in the file it names; the auditor reports
only failures; the auditor estimates a ratio; a clean fixture produces a finding;
the checker reaches a network or a model; or a cold reader cannot get a result
without being coached.

## The gates, named before they are written

| Gate | What it proves | How it can fail |
|---|---|---|
| SHAPE | `auditor/` holds the declared set and nothing else | a stray file |
| PROVENANCE | every cited provision and definition is on disk, dated, hashed, with the W3C status line | a missing or undated file |
| ANCHOR | ratio math matches published boundary values | a wrong luminance formula |
| MUTATION | each rule goes red on input built to break it | a rule that never fires |
| SILENCE | compliant input produces zero failures | an invented finding |
| INVARIANCE | one violation, several spellings and stylesheet forms, identical verdicts | a syntax-dependent verdict |
| PURITY | the checker imports nothing that reaches out | a hidden network or model call |
| CITATION | each finding's criterion exists, its quote is verbatim, its level matches, its kind fits, and its ratio recomputes | a planted citation slips through |
| EXAMPLES | every fenced output in examples.md equals a live run | a hand-edited example |
| TERRITORY | real public brand token files re-audit to committed verdicts | drift between code and receipts |
| DIFFERENTIAL | an independent luminance implementation agrees on every pair | a math error in either |

`check.py` prints the count of gates checked and passed. The README pastes that
line; it never types a number.

## The fixtures

- `fixtures/clean.json`: four elements, all compliant. Expected: PASS, 0 failures.
- `fixtures/violating.json`: three failures and one undecidable. Expected: FAIL, exit 1.
- `fixtures/brands/*.json`: built once from public design-token files carrying
  VoltAgent catalog provenance, brands named, attribution per file. Expected
  verdicts committed to `receipts/EXPECTED-brands.json`. Five pairs are checked by
  hand against a second public calculator before the territory gate is written.
- `examples/findings-broken.md`: one valid finding and three planted bad
  citations. Expected: bare `python3 check.py` catches exactly three, names each.

## Run order, fixed

0. Freeze this file (this commit).
1. Restructure, reference/ completeness, gates, fixtures, defect fixes. Every
   commit must leave `check.py` green except where a gate is shown red on purpose,
   and that red run is pasted into `receipts/DEVIATIONS.md`.
2. Run A, clean clone: clone into an empty directory, run `python3 check.py`,
   paste the whole output into `receipts/CLEAN_CLONE.md`.
3. Run B, stranger: one named person outside the project, chosen before the run
   (Ciaran, software-literate, has never seen the repo). He receives the repo URL
   and one sentence. Screen and audio recorded. No hints. The only permitted reply
   to a question is "whatever you think it means". If that rule is broken, the
   break stays in the transcript and the receipt says so. Hard stop at 25 minutes,
   or a located finding, or a give-up. All three are valid, published outcomes.
   Transcript to `receipts/RUN_B_STRANGER.md` verbatim, typos kept. Then
   `auditor/README.md` is rewritten from where he stalled; the old version is kept
   at `receipts/README-v1.md`; both word counts recorded.
4. Run C, cold model: a fresh Claude session with `auditor/` attached and a brand
   fixture that appears nowhere in examples.md. Prompt: "Audit this." Run twice:
   once where the model can execute the checker, once where it cannot. Expected
   findings committed before the run. Transcripts to `receipts/RUN_C_COLD_MODEL.md`
   unsmoothed.

No run is repeated to get a better result. If one is repeated, both are published
and the reason is stated.

## What "broke" means

A correction is any change to a file inside `auditor/` traceable to a run. The
count is the number of such diffs and is published whatever it is. A change not
prompted by a run is listed separately with its own reason.

## What this method cannot prove

The citation gate proves a cited provision exists and its quote is verbatim. It
cannot prove the citation is the right one for the element in front of it. That
judgment stays human, and the gate says so in its own output.
