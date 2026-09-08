# Comp 12 finish specification and execution plan

Approved by Alex on 2026-09-08. Baseline: f851b5d. Work: W-20260908-wcag-contrast-auditor-comp-12-auditor-entry-fi-d8c490.

## Decision and verifier

Finish the existing WCAG contrast auditor, preserving SC 1.4.3 and 1.4.11 at AA and SC 1.4.6 as AAA headroom. A reviewer must be able to reproduce the measurements, check citations against the shipped standard, and see honest raw evidence. Winning is an aspiration, not a completion claim.

Verifier: every required local and CI gate passes on the tested commit; all 60 frozen AI conformance trials pass their assertions; Ciaran's recorded no-help test exists. A recorded human failure is evidence, not usability success. Completion remains open until that outcome is recorded and any resulting defect is resolved. Alex alone sends the invitation and competition comment.

Target draft: 2026-09-10. Published deadline: 2026-09-11 23:59 EST; target before 23:59 America/New_York conservatively. Premium was confirmed in the signed-in Skool plan page this session. Repo is already public.

## Global Constraints

- Runtime remains Python standard library only, offline and without API keys. Development and evaluation tools are separate.
- Preserve TEST_METHOD.md exactly from commit 0b57525. Append deviations, never rewrite the frozen method or fabricate transcripts.
- Preserve the drop-in folder's six existing entries, including checker/. No website, server, new criteria, or client material.
- Audit exit 0 means complete PASS; 1 means an AA failure (takes precedence over unknowns); 2 means INCOMPLETE or invalid input. AAA misses use [aaa ], never [FAIL].
- One implementer writes at a time. Subagents never mutate Git state or spawn agents. The lead owns commits, pushes, reviews, and pathway records.
- All confirmed behavioral defects get a failing regression before a fix. Retain red output and the subsequent green output.
- No private corpus or session context enters public assets or model evaluations. Design vault and software-factory are read only.
- Ciaran is the only human tester. No silent substitute, invented receipt, or completion without his run. Alex sends all messages.
- Scope stays within this repository, its competition draft folder, and the existing central work ledger. Do not rewrite global tools to satisfy this repo's checks.

## Baseline and premortem

Read-only audit verified 131 checks / 11 gates locally; Windows CI at f851b5d failed seven reference checks. Default Windows decoding changes the UTF-8 notice before re-encoding and hashing. The reference fetch hash matches live W3C bytes. The current citation parser accepts forged N/A, ignores opacity, skips malformed heads, loses spaced RGB values, and can crash on malformed size. Normalization coerces false strings to bold, accepts infinity, and strips incompatible units. Fractional RGB channels are rounded prematurely.

| Failure outcome              | Assumption exposed              | Observable evidence                                    | Revision                                                     |
| ---------------------------- | ------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Judge cannot run on Windows  | Host encoding equals UTF-8      | Seven failed reference checks in live CI               | Explicit encoding, LF bytes, six matrix jobs                 |
| Forged finding is approved   | Parsed content is complete      | Fake N/A and opacity accepted; malformed head vanishes | Strict parser, complete input, recomputation, source binding |
| Public proof is unverifiable | Summaries equal raw transcripts | Old clean clone says 114; README says 131              | Preserve history, append raw runs with SHA                   |
| Brand claim exceeds evidence | Token roles prove rendered use  | Ambiguous pairs drive 40 of 48 FAIL scenarios          | Pinned public inputs, visible assumptions, scenario wording  |

## Phase gates and ownership

Each Task is a bounded implementer assignment followed by a spec-and-quality reviewer. Lead records BASE before dispatch and verifies evidence after report. Implementation tasks are sequential. Read-only reviews and bounded research may overlap independent lead work. Keep substantive slices under 25 manually changed files / 800 net lines where feasible; generated fixtures and raw receipts are separately reviewed data batches, not an excuse to enlarge code diffs.

## Task 1: Portable references and CI regression floor

Own .gitattributes, explicit text encoding in the Python entrypoints/checker/reference builder, tests/test_portability.py, .github/workflows/check.yml. Add standard-library unittest discovery without replacing check.py or removing existing gates. Test UTF-8 notices under a Windows-like default encoding and LF byte identity. All source reads/writes that consume or generate project text use UTF-8 explicitly. Pin LF for text artifacts and hash the committed reference bytes consistently; reference fetch writes UTF-8 LF. Keep W3C excerpts and TEST_METHOD byte-identical. Show regression red before fixing. CI matrix remains ubuntu/windows/macos × Python 3.10/3.13, fail-fast false, exact exit 1 for planted rejection (do not accept a crash); run unittest discovery and check.py. Report commands, full test output, scope, and limitations to assigned report file. Lead pushes this slice and verifies all six jobs before Task 2.

## Task 2: Strict element normalization and numeric correctness

Own auditor/checker/contrast.py, auditor/checker/audit.py normalization only, tests/test_inputs.py, relevant check.py assertions. No report-parser edits yet. Require real booleans; finite positive font sizes; suffix px only in font_px and pt only in font_pt; reject inconsistent simultaneous sizes or bold/weight declarations. Numerically equivalent dual declarations may pass. Preserve fractional RGB channels and reject malformed/nonfinite/out-of-range channels and alpha; only alpha exactly 1 is opaque. Relative weight names bolder/lighter need inherited context and are UNDECIDABLE. Numeric font weights must be finite and in CSS range 1..1000. Reject non-string colors through ColorError. Test exact 14pt bold and 18pt regular boundaries without rounding conversions prematurely, near 4.5 and 3 thresholds, NaN/inf/zero/negative sizes, booleans and units, opacity bounds, unknown kinds and malformed mixed elements. Existing fixtures remain stable unless an actual defect changes a verdict; document any change. Show red then green.

## Task 3: Lossless findings and strict source-bound citation validation

Own auditor/checker/findings.py, audit.py rendering/report fields, check.py CLI/citation gate, tests/test_findings.py, tests/test_cli.py, auditor/{README,rules,examples,identity}.md for this interface. Emit input: JSON with typed fields, preserving enough original invalid data to verify an UNDECIDABLE result. Read existing valid legacy key=value reports with a compatibility parser including spaced RGB. Reject malformed finding-like heads, empty reports, duplicate required fields, unknown/duplicate input keys that affect meaning, missing or nonfinite measurements, and malformed sizes with named errors instead of crashes. Recompute every status including N/A/UNDECIDABLE/AAA from all inputs; compare criterion, level, measured/required ratio, severity, relevant quote/exception, and provision. Preserve required ratios for N/A/unknown and prohibit measured ratios there. Keep report header and summary consistency when present; do not treat arbitrary prose as findings.

Public command: python3 check.py REPORT [--against PAIRS] [--mode measured|no-execution]. Default measured. Source binding requires one source element identity per id, rejects duplicate ids, altered/missing/extra elements and missing required criterion findings; compares all material raw/normalized fields. A source document must be a JSON list or existing {elements: [...]} shape. In no-execution mode every element has one AA UNDECIDABLE finding with source-derived criterion, relevant quoted threshold, no measured ratio, severity unknown, and report INCOMPLETE. The citation validator exits 0 for a valid no-execution report (it verified the report, not compliance), 1 for a rejected report, 2 for unreadable CLI input. Document this distinction. JSON machine format of audit.py remains compatible except additive fields when required. Full audit exits remain 0/1/2 as global constraints.

Reference paths must remain inside reference/, including manifest-controlled paths and symlinks; fail closed on missing/invalid manifest and mismatched inventory/hash. Tests cover every existing attack, forged exemptions, opacity, missing numeric claim, wrong requirement or exception quote, malformed headers alone/among valid findings, invalid input size, omission, duplication, altered source, spaced RGB/RGBA, Unicode, and all checker-rendered status round trips. Regenerate tagged examples from actual execution; historical receipts stay historical. Keep the three planted bad findings demonstrably rejected. Show red then green.

## Task 4: Public fixture provenance and scenario claims

Own fixtures/build_brand_fixtures.py, fixtures/brands/*.json, receipts/EXPECTED-brands.json, tests/test_fixtures.py and relevant TERRITORY/DIFFERENTIAL checks. Use the existing pinned public catalog commit, derive both colors and typography from public bytes, and record public token paths plus explicit role/size assumptions. No private local metadata leaks. Preserve the named cohort where source supports it; log changed/skipped inputs and regenerated counts. Remove implicit rem=16: require an explicit builder root-size option or leave size unknown. Store the actual public input hash, verify upstream content, and distinguish scenario assumptions from source facts. Missing typography stays unknown. Developer-only PyYAML stays outside runtime. Gate expected cohort and all elements, reject extra/missing expectations; compare every opaque supported color against independent oracle. Render README descriptions as catalog token scenarios, never assertions about live brand sites. Show provenance/assumption regressions red then green and preserve old result counts as historical.

## Task 5: Development coverage and reproducible AI evaluation harness

Own dev requirements/config, scripts/coverage_gate.py, tests/test_coverage_gate.py, evaluation runner/grader under evals/, test coverage for these tools, CI coverage job, ops/audit/STATUS.md. Install pinned development-only coverage in an isolated venv; runtime commands keep zero installs. Enforce changed executable line coverage >=80% and changed branch coverage >=70% against f851b5d; also report totals so the gate cannot hide new files. Test positive and negative controls of the coverage gate. Require it on PR. Record framework tooling mismatch as N/A: no web UI so Lighthouse/axe/JS bundles are not applicable. Standard unittest command resolves rails detector's failure to recognize the original custom runner. No edits to global rails-check.

Freeze six JSON cases and answer assertions before model calls: compliant; AA failures; AAA-only misses; exemptions; undecidable inputs; misleading ratio/instruction fields. Five fresh runs of each per mode =60. Keep repeated trials distinct. Hermetic neutral cwd with only auditor/ and one fixture, no repository memory/settings/history/private files/answer key; pinned system prompt, disabled inherited settings, approved executable checker-only tool access in measured mode and read-only access in no-execution mode. Save exact command, model id, prompt, stdout/stderr, tool trace, errors, input/output hashes, and parsed grader result. Grade with --against and explicit mode plus no-network/no-invented-measurement/coverage assertions. Wrong/missing output is failure, never skipped. Network calls to the model provider are allowed only in the development runner; auditor itself stays offline. Runner is bounded and can resume completed trial ids without rerunning. Validate harness on one smoke trial per mode before the fixed 60; smoke trials are marked pilot and cannot count. Do not launch 60 until the lead has committed the fixtures/expectations and reviewed isolation. Provide exact launch command and artifact schema; lead runs trials.

## Task 6: Honest receipts, README and submission package

Own receipts documentation and README prose only after preceding interfaces/data stable; update competition drafts through lead. Preserve old snapshots and add dated corrections: cold receipt is summaries, clean clone is abridged/old, correction count claims disagree with table. Recover original raw transcripts if actually available; otherwise label unavailable and publish new raw runs separately. No fabricated result or coaching-free claim. Prepare Ciaran kit (candidate SHA, README-v1 copy, exact prompt, 25-minute stop, recording/transcript placeholders explicitly pending) without sending. Three-sentence bare submission draft uses verified claims, repo link and Claude Code/Codex authorship disclosure; omit volatile counts and unfinished receipts. No published claim of readiness until all required proof exists. Lead captures complete clean-clone logs, final SHA CI and outside-the-commit attestation; documents all remaining blockers.

## Final review and release

Lead runs whole-candidate independent Codex and GLM critique with the same scoped public diff and brief; Claude-family reviewer substitutes if GLM is unavailable, with the family gap named. Each reviewer checks correctness, security, DRY/KISS/YAGNI/SOLID/SINE and evidence truth. Confirm findings by executing their cases, repair test-first via implementer and scoped reviewer. Freeze any added evaluation before reruns. Preserve all attempts. Require final current public SHA CI success, complete fresh clone output, all 60 trial assertions, and Ciaran's recorded outcome. Merge/push under user's implementation approval after checks; do not post or send. Keep outcome open while human evidence is missing and report partial technical readiness honestly.

## Plain-English Summary

### What we're building

A color checker that shows its work against published rules.

### Why this piece

Judges need results they can check on their own computers.

### The surprise

Local checks passed while the Windows run failed.

### The real problem I caught

Some false reports passed checks. New tests will expose each fault.

### Where we are right now

The approved repairs are starting in a separate copy.

### The one thing left

Fix and prove each step. Ciaran's recorded test remains required.
