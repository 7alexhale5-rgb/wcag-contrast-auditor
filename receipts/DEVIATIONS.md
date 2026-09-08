# DEVIATIONS and red runs

Dated log of everything that turned out wrong after TEST_METHOD.md was frozen (commit 0b57525), and of every gate deliberately shown red so a green run means something. Nothing here is smoothed.

## Defects found before any outside run (2026-09-08, found by running the repo, not by reading it)

| # | Defect | How it was proved | Fixed in |
|---|---|---|---|
| D1 | AAA misses rendered as `[FAIL]` | `python3 auditor/checker/audit.py fixtures/violating.json` printed `[FAIL] muted caption SC 1.4.6 (AAA)` | render() prints `[aaa ]`; SILENCE gate asserts no `[FAIL]` line carries AAA |
| D2 | Empty `examples/` directory beside `examples.md` | `ls -la` | replaced by `examples/findings-broken.md` |
| D3 | examples.md said "pasted unedited"; example 1 dropped a line, example 2 dropped the header and AAA lines, example 3 rewrapped | diff against a live run | examples.md regenerated from live runs; EXAMPLES gate compares byte for byte |
| D4 | README said 27 checks; the instrument printed 25; docstring said four classes and listed five | `grep -c "^  ok"` = 25 | check.py prints its own count; README pastes it |
| D5 | Severity boundary was `0.67` in code, "two thirds" in rules.md; 3.0:1 on 4.5 was blocker in code, major in prose | `_severity(3.0, 4.5)` returned blocker | `required * 2 / 3`; MUTATION gate tests exactly 3.0 on 4.5 |
| D6 | INCOMPLETE verdict exited 0, so an undecided audit passed CI silently | `#767676` with no font size: INCOMPLETE, exit 0 | exit 2 for INCOMPLETE; SILENCE gate |
| D7 | UNDECIDABLE always cited 1.4.3, even for non-text | audit.py line 45 | cites the criterion for the element kind; MUTATION gate |
| D8 | Every reference file header embedded the fetch date, so re-fetching on a later day dirtied unchanged provisions and the README claim about `git diff reference/` was false | fetch-standard.py lines 63-64 | date and page hash moved to MANIFEST.json |
| D9 | "Code: MIT" with no LICENSE file; W3C notice lacked the document status | `ls` | LICENSE added; `Status: W3C Recommendation 06 May 2025` on every file |
| D10 | The standard's exceptions (logotype, incidental, inactive) were on disk but not in code; a logo wordmark got FAIL | no exempt path in audit.py | `exempt` field yields N/A quoting the clause; never inferred |
| D11 | Reference text is hard-wrapped ("significant\n other"), so a naive substring check would reject an honest quote | wcag21-1.4.3.md | citation gate normalises whitespace |
| D12 | Brand token pool held 21 files without catalog provenance, including client brands | `grep -L VoltAgent` | territory fixtures filtered to catalog-provenance files only |
| D13 | 52 of 83 token files carry an alpha colour somewhere | grep | alpha pairs come out UNDECIDABLE, never skipped |

## Gates shown red on purpose (2026-09-08)

Each block: the one-line sabotage, the red output, then the restore. A gate that has only ever run green has proved nothing.

### Severity boundary put back to 0.67
```
  FAIL  exactly two thirds of the bar is major, not blocker  <- blocker
99 checks in 9 gates: 98 passed, 1 failed
GATE FAILED
```

### One character changed inside a pasted example
```
  FAIL  full output for fixtures/clean.json equals a live run byte for byte
99 checks in 9 gates: 98 passed, 1 failed
GATE FAILED
```

### One planted citation corrected, so only two remain
```
  FAIL  planted nonexistent SC is caught by check A
  FAIL  exactly three of four findings rejected  <- ['ghost border', 'no size given']
99 checks in 9 gates: 97 passed, 2 failed
GATE FAILED
```

### A provision file edited by one line
```
  FAIL  large-scale-text: file hash matches the manifest
99 checks in 9 gates: 98 passed, 1 failed
GATE FAILED
```

After each restore:
```
99 checks in 9 gates: 99 passed, 0 failed
GATE PASSED: every rule was shown to fail on purpose, stay quiet on compliant
input, hold across five spellings, cite only what is on disk, and recompute.
```

### One committed brand verdict changed from FAIL to PASS
```
  FAIL  no fixture drifted from its committed verdicts  <- ['airbnb']
114 checks in 11 gates: 113 passed, 1 failed
GATE FAILED
```

### The vendored oracle nudged by one coefficient
```
  FAIL  zero disagreements beyond 0.01  <- [('airbnb', 'on-primary on primary', 3.52, 3.49), ('airbnb', 'ink on canvas', 15.91, 15.8), ('airbnb', 'body on canvas', 10.53, 10.48)]
114 checks in 11 gates: 113 passed, 1 failed
GATE FAILED
```

After restore:
```
114 checks in 11 gates: 114 passed, 0 failed
GATE PASSED: every rule was shown to fail on purpose, stay quiet on compliant
input, hold across five spellings, cite only what is on disk, and recompute.
```
