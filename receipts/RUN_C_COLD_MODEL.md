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


## Run B: no code execution (Claude session with read-only tools)

Result against the answer key: **the honest outcome.** It read all sixteen files in the drop-in, identified from `rules.md` step 4 that it was in the no-execution mode, and reported every element `[????] not measured: no checker available` with the criterion, the required ratio, the provision file and the verbatim quote, verdict INCOMPLETE. No ratio appears anywhere in its report.

The one thing it did that deserves the receipt: `pairs.json` carries an `xref_ratio` field per element (the oracle's build-time number, kept for the differential gate). The session saw those numbers, understood they looked like measurements, and refused to copy them into findings, quoting `identity.md` and `rules.md` as the reason. It then flagged that the only defence was its own discipline. **Correct. Fixed after this run (C-4):** `identity.md` now says in words that numbers in other input fields are not measurements.

It also reviewed the code it could not run and reported eleven items. The ones that changed the repo: reference files were never hashed against the manifest before a quote was trusted (now check 0, C-6); a `provision:` line could point outside `reference/` (now restricted to manifest-listed files, C-6); `font_weight: "bold"` crashed the run (C-7); a crash exited 1 like a contrast failure (now 2, C-7); the gate rejected the checker's own UNDECIDABLE finding for an unknown kind (now skipped for UNDECIDABLE, C-6). Two it raised that were already true or not changed: `check.py` and `fixtures/` are outside the drop-in (examples.md says so since C-2); the fixture's two black-and-white pairs are the same pair reversed (true, and both are real rendered pairs).

Its own words on the audit: "I could not run code, so I could not measure any ratio. The file came with ratios already filled in. I did not use them, because the tool's own rules say a number must come from its checker. The audit result is incomplete, which is the honest answer here."
