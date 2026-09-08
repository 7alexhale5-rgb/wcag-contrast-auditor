# Test addendum, 2026-09-08

The frozen TEST_METHOD.md at 0b57525 stays unchanged. Alex approved the finish plan after the baseline audit exposed faults its original checks missed. This addendum discloses revised methods before the new model trials.

1. Run regressions before each behavioral fix, retain red and green outputs, and review the change independently. Run the six existing OS/Python combinations after portability repair. Subsequent final-release checks must include that same matrix.
2. Add source-bound report verification, strict malformed-input rejection, explicit no-execution validation, full criterion recomputation, and development-only changed coverage thresholds of 80% lines and 70% branches.
3. Derive catalog scenario inputs from pinned public source bytes, with named token paths and pairing/root-size assumptions. Results describe those scenarios and never prove a live website fails.
4. Freeze six cases and graders before any new evaluation. Run five fresh trials per case per mode, 60 trials total. Save full observable prompts, responses, tool traces, permissions and model IDs. Pilot attempts are separate; failures, interrupted starts and repeats are disclosed. This is conformance testing, not a claim of statistical superiority.
5. Preserve the candidate README for Ciaran's recorded no-help run. Ciaran remains the sole human tester; use the original minimal prompt and 25-minute stop. Alex sends the invitation. Record an unsuccessful run honestly. Any revised README and repeated run get separate receipts.
6. Preserve older receipts and correct claims through dated additions. The older clean-clone receipt is not proof of the final release. Capture complete fresh-clone output and CI for the final public SHA; keep the last attestation outside that tested commit.

## Completed evidence

Portability was repaired in f19aeb6; independent review found an exit-1 crash could masquerade as the planted rejection. Commit 7310355 requires exit 1, the exact rejection summary, and empty stderr. All six jobs in GitHub run 34269111360 passed on 7310355. Raw tests and review are retained in receipts/comp-12-finish/task-1-*.

## Open evidence

The new 60-trial evaluation and Ciaran run have not occurred. Historical raw cold-run logs were located, including failed starts and a repeat. Extraction and public-scope review are pending. No original transcript has been reconstructed.
