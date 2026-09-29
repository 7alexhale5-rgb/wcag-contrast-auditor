# WCAG Contrast Auditor

> Status: active | Type: infra (Clief Notes Comp 12 entry, dependency-free Python)

Drop `auditor/` into a Claude project, hand it colour pairs, get back what passes, what fails,
by how much, and which WCAG 2.1 success criterion says so, with the provision text alongside it.
No API key, no network, no install beyond Python 3 stdlib.

## Where to go

This repo follows ICM (Jake Van Clief's folder method): this file routes, each room's
`CONTEXT.md` holds its contract.

| Task                                                              | Go to       | Read                                       | Skills          |
| ----------------------------------------------------------------- | ----------- | ------------------------------------------ | --------------- |
| Change the checker, its rules or citation logic                   | `auditor/`  | [auditor/CONTEXT.md](auditor/CONTEXT.md)   | `/review-stack` |
| Add or edit test colour pairs / brand fixtures                    | `fixtures/` | [fixtures/CONTEXT.md](fixtures/CONTEXT.md) | none            |
| Record or read a verified run (clean clone, sabotage, cold model) | `receipts/` | [receipts/CONTEXT.md](receipts/CONTEXT.md) | none            |
| Show or extend the sabotage/citation demo                         | `examples/` | [examples/CONTEXT.md](examples/CONTEXT.md) | none            |

Root files stay put: `check.py` (the entry point every README command names), `README.md`,
`TEST_METHOD.md`, `LICENSE`, `.github/workflows/` (CI).

## Naming

Python snake_case, docs kebab- or SCREAMING-case to match existing receipts, `.md`/`.json` pairs
where a receipt has an expected-value companion.
