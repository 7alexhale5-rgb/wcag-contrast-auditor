# RECEIPT: cold model runs

Answer key committed first: `receipts/EXPECTED-cold-model.md` (commit 7a929c2). Fixture: the Mintlify brand token file, which appears nowhere in `auditor/examples.md`. Each run was a fresh Claude session given a directory holding only `auditor/` (as committed at 7a929c2) and `pairs.json`. Prompt, verbatim: "There is a folder auditor/ and a file pairs.json. Audit this. Report your findings in full, verbatim. Say what you read, in order, before the findings." Nothing else. Transcripts below are the sessions' final reports, unedited.

## Run A: checker available (Claude Code, can execute Python)

Result against the answer key: **match.** Same two passes, same two failures, same criteria, same ratios (19.7, 19.7, 2.3, 1.2), verdict FAIL, exit 1. Citation gate on its own output: 5 checked, 0 rejected.

Three things the model said that the checker did not, kept because two of them changed the repo:

1. The `xref_ratio` values in the fixture (19.8, 2.37, 1.26) differ from the checker's (19.7, 2.3, 1.2) in the last digit. It recomputed the exact ratios and found the difference is the rounding rule (the checker floors to one decimal so 4.4999 never reads as 4.5; the oracle rounds to two). No verdict changes. Correct, and no change made.
2. The two failures are the two pairs the fixture itself flags as ambiguous (`muted`, `hairline`). It noted the checker had no exemption name for a decorative divider under 1.4.11, only `inactive`. **Correct. Fixed after this run:** `"exempt": "decorative"` on a non-text element now yields N/A quoting the "required to identify" clause, and a gate exercises it. Logged as a correction traceable to Run C in `DEVIATIONS.md`.
3. `examples.md` said `check.py` re-runs each fixture, but neither `check.py` nor `fixtures/` is inside the drop-in, so a reader of the folder alone could not run the self-check it describes. **Correct. Fixed after this run:** `examples.md` now says where those live.

Transcript of what it read, in order: `auditor/README.md`, `identity.md`, `rules.md`, `examples.md`, `checker/audit.py`, `checker/contrast.py`, `checker/findings.py`, `reference/MANIFEST.json`, `reference/fetch-standard.py`, the three SC files, the three glossary files, `pairs.json`. Then it ran `python3 checker/audit.py ../pairs.json` from inside `auditor/`, the `--json` form, the citation gate on the saved report, and a SHA-256 check of all six reference files against the manifest (all matched). It did not re-fetch w3.org and said so: currency against the live standard was "carried forward from the manifest, unverified."

Its own verbatim checker output equals the answer key byte for byte (checked with `diff` on 2026-09-08, including the three `note:` lines).

