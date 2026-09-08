# Comp 12: current evidence and next move

Updated 2026-09-08. Public entry: https://github.com/7alexhale5-rgb/wcag-contrast-auditor. Work branch: codex/comp-12-finish. This page reports evidence, not submission readiness.

## What we're building

An offline color checker with findings that judges can reproduce and challenge.

## Why this piece

The previous local checks missed Windows failures and accepted forged reports. The repair sequence fixes those faults before any new success claim.

## The surprise

The six platform checks now pass, but independent review continues to find boundary cases. New failing tests are retained before each repair.

## The real problem I caught

| Failure chain | Evidence | Current treatment |
|---|---|---|
| Windows hashes decoded text differently | Original Windows CI failed seven reference checks | Fixed UTF-8/LF/raw hashing; all six jobs passed at7310355 |
| A crash can look like a successful rejection test | RuntimeError yielded child1 and test-step0 | Require exact rejection summary, child1, empty stderr; canaries pass |
| Invalid sizes and opacity produce false PASS | New unit-test red runs; exact size review reproduction | Fixed with exact size comparisons and named refusals; reviewed at2ee0596 |
| False citations and omitted elements are accepted | Baseline hostile probes | Strict parser/source binding next |
| Brand assumptions become website claims | Public source audit and builder inspection | All58 source mappings found; rebuild provenance still pending |
| Summaries are presented as transcripts | Historical receipts compared with original logs | Five original dispatch logs located; extraction pending |

## Where we are right now

| Approved step | State | Evidence needed next |
|---|---|---|
| Specification | Approved and recorded | Govern proofP-47c8be25ee3f; frozen method unchanged |
| Portability | Complete | [Six-platform CI34269111360](https://github.com/7alexhale5-rgb/wcag-contrast-auditor/actions/runs/34269111360) |
| Inputs and citations | In progress | Input repair reviewed; citation core and source-bound report tests next |
| Fixture provenance | Research complete; implementation pending | Pinned public derivation, mutation and oracle tests |
| Model evaluations | Not started | Freeze six cases, prove isolation pilots, run all60 |
| Ciaran test | Pending | Recording, verbatim transcript, preserved README and honest outcome |
| Final package | Pending | Final public SHA checks and complete fresh-clone receipt |

The model-isolation researcher proved a local OS policy can deny private-file reads and network connections while running the checker. A full model pilot must still prove the intended tool boundary. No model trial has run under the new method.

## The one thing left

Finish each repair and retain its proof. Ciaran must still run the test. Alex sends the invite and posts the entry. Submission is not ready or posted.
