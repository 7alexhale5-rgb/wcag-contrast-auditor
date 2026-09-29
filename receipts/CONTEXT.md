# Receipts room: verified run evidence

One job: the pasted, dated proof that a claim in the README or a rule change is real.

## Inputs

- The run to record: `python3 check.py` output, or a targeted sabotage run.
- Existing receipts to update: `receipts/CLEAN_CLONE.md`, `receipts/DEVIATIONS.md`,
  `receipts/RUN_C_COLD_MODEL.md`, `receipts/EXPECTED-*.{md,json}`.

## Process

1. Run the command being proved from a genuinely clean clone or cold context.
2. Paste the full, unedited output into the matching receipt file with the date.
3. For a new failure-mode demo, add it to `receipts/DEVIATIONS.md` rather than a new file.

## Outputs

- An updated receipt `.md` (and its `EXPECTED-*` companion when one exists) with a real, dated,
  unedited run transcript.

## Human check

Alex re-runs the same command and diffs against the pasted receipt. Pass: output matches (or the
receipt is re-pasted current). Fail: the README's falsifiability claim is now false — fix first.
