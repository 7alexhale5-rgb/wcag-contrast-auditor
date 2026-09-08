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

## Corrections traceable to a run (2026-09-08)

Per TEST_METHOD.md, a correction is any change inside `auditor/` traceable to a run. Count so far: **3**, all from Run C-A (cold model, checker available).

| # | From | Change inside auditor/ | Why |
|---|---|---|---|
| C-1 | Run C-A | `checker/contrast.py`, `checker/audit.py`: added `decorative` as a named non-text exemption, N/A quoting the 1.4.11 "required to identify" clause | the model found no exemption name for a decorative divider; the only non-text one was `inactive` |
| C-2 | Run C-A | `examples.md`: says where `fixtures/` and `check.py` live | they are outside the drop-in, so a reader of the folder alone could not run the self-check it described |
| C-3 | Run C-A | `identity.md`: one paragraph on out-of-scope (decorative, logotype) as distinct from undecidable | follows from C-1 |
| C-4 | Run C-B (judgment-only) and hostile review | `identity.md`: "report that you could not measure, and stop" replaced with the two-mode rule, so it no longer contradicts `rules.md` step 4; the paragraph also names that numbers in other input fields are not measurements | the judgment-only session flagged the `xref_ratio` field as a trap for a reading model; it did not fall for it, but the defence was only its discipline |
| C-5 | Run C-B | `examples.md`: example 5, the judgment-only shape, with no ratio anywhere | no worked example of mode B existed |
| C-6 | hostile review | `checker/findings.py`: check 0 (every reference file hashes to the manifest before any citation is judged), B_FILE_MISMATCH (criterion must live in the file cited), I_NO_INPUT, H_UNKNOWN_MARK, F_SEVERITY_MISMATCH, AAA lines recomputed, provision restricted to manifest-listed files, indented heads parsed, malformed input lines rejected instead of crashing | four ways a planted citation got through, one path traversal, one crash |
| C-7 | Run C-B and hostile review | `checker/contrast.py`, `checker/audit.py`: `font_weight: "bold"` and `font_px: "16px"` read instead of crashing; 8-digit hex parsed with the alpha rule; alpha above 1 refused; an unreadable element is one UNDECIDABLE finding; a crash in `main()` exits 2, never 1 | tracebacks on ordinary CSS values; a crash read as a contrast failure in CI |
| C-8 | hostile review | `reference/*.md`: the source page's own copyright notice line added to every header (W3C Document License asks for the pre-existing notice) | licence notice was incomplete |

Uncorrected edits, not prompted by a run, with their reasons: the fixture builder now pins an upstream commit and reads each brand's catalog path from its own provenance line (openai dropped: its local copy came from the company site, not the catalog; anthropic maps to `claude`, xai to `x.ai`); `check.py` prints a neutral count instead of a claim on a green run.

## Answer-key drift, disclosed

`receipts/EXPECTED-cold-model.md` was generated at 7a929c2 and prints `bold=false` on the non-text hairline line. After C-7 the checker no longer prints a bold field for non-text elements, so a re-run today differs from the key by that one token on one line. The key is not regenerated, per the method; Run A matched it byte for byte at the time, and this paragraph is the record of what changed after.

## The remaining gates shown red (2026-09-08, after the hostile review noted only six of eleven had been)

Bytecode caching disabled for these runs: an earlier capture reused a stale module because the sabotage and its restore fell within one second at equal file size, and the phantom failure leaked into the next block. Those captures were discarded and redone.

### SHAPE: a stray file dropped into auditor/
```
  FAIL  auditor/ has nothing undeclared  <- extra ['notes.txt']
131 checks in 11 gates: 130 passed, 1 failed
```

### ANCHOR: the luminance formula given the wrong red coefficient
```
  FAIL  #000000 on #ffffff == 21.0:1  <- got 21.2
  FAIL  full output for fixtures/clean.json equals a live run byte for byte
  FAIL  full output for fixtures/violating.json equals a live run byte for byte
  FAIL  no fixture drifted from its committed verdicts  <- ['airbnb', 'airtable', 'anthropic', 'apple', 'binance']
```

### MUTATION: the large-text exception disconnected
```
  FAIL  large-text exception actually changes the verdict  <- 16px=FAIL 32px=FAIL
  FAIL  font_pt 18 is large text (24px), font_px 18 is not  <- pt=FAIL px=FAIL
  FAIL  font_weight 700 is bold, 600 is not  <- 600=FAIL 700=FAIL
  FAIL  font_weight 'bold' and font_px '19px' are read, not crashed on  <- FAIL
  FAIL  full output for fixtures/clean.json equals a live run byte for byte
```

### SILENCE: an AAA miss printed as [FAIL] again (defect D1 reintroduced)
```
  FAIL  an AAA miss is never printed as [FAIL]
  FAIL  an AAA miss is printed as headroom
```

### INVARIANCE: three-digit hex parsing removed
```
  FAIL  all five spellings produce the same verdict  <- ['FAIL', 'UNDECIDABLE', 'FAIL', 'FAIL', 'FAIL']
  FAIL  all five spellings produce the same ratio  <- [4.4, None, 4.4, 4.4, 4.4]
131 checks in 11 gates: 129 passed, 2 failed
```

### PURITY: a network import added to the checker
```
  FAIL  auditor/checker/contrast.py imports nothing that reaches out  <- found {'urllib'}
131 checks in 11 gates: 130 passed, 1 failed
```

### CITATION check 0: one byte appended to a reference file, then a valid report checked against it
```
REJECTED reference/  0_REFERENCE_TAMPERED: reference/wcag21-1.4.3.md does not match MANIFEST.json

reference/ does not match its manifest; no citation can be trusted until it does
```

After each restore:
```
131 checks in 11 gates: 131 passed, 0 failed
GATE PASSED. What each gate proved is in its own lines above; what a gate
looks like when it fails is in receipts/DEVIATIONS.md.
```

## Finish-plan method revision (2026-09-08)

The approved finish work uses [.planning/comp-12-finish/TEST_ADDENDUM.md](../.planning/comp-12-finish/TEST_ADDENDUM.md). The original TEST_METHOD.md is byte-identical to 0b57525. Portability regressions and the crash-versus-rejection canary, their raw outputs, and independent review are preserved in [comp-12-finish/](comp-12-finish/). All six OS/Python jobs passed at 7310355 in run 34269111360.

Correction to the earlier count: the table above lists eight entries, C-1 through C-8. Its preceding “3” sentence was stale. Those eight historical correction entries are separate from the new finish-plan defects and fixes; they are not a count of independent human runs.
