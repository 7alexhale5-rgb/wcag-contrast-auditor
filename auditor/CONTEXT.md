# Auditor room: the shipped checker package

One job: the contrast-checking logic and its provision citations — what ships when someone drops
`auditor/` into their own project.

## Inputs

- Rule logic and citations to change: `auditor/checker/`, `auditor/rules.md`, `auditor/reference/`
  (WCAG provision text), `auditor/identity.md`.
- Usage contract for consumers: `auditor/README.md`, `auditor/examples.md`.
- Missing input: a rule change with no cited SC number is not written.

## Process

1. Edit the checker logic in `auditor/checker/`; keep every pass/fail cited to the SC in
   `auditor/rules.md` and quoted from `auditor/reference/`.
2. Run `python3 check.py` from the repo root; it must stay at 131/131 (or the new total) passed.
3. If citation text changed, verify it against `auditor/reference/` verbatim — no paraphrase.

## Outputs

- Changed files under `auditor/checker/`, `auditor/rules.md`, `auditor/reference/`.
- A passing `python3 check.py` run.

## Human check

Alex reads the `check.py` summary line. Pass: all gates pass and no citation was invented or
paraphrased. Fail: the run exits non-zero and names the line; fix before merge.
