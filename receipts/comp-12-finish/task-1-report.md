# Task 1 report: portable references and CI regression floor

## Changes

- `.gitattributes` pins detected text to LF on checkout (`* text=auto eol=lf`).
- Every project-text file read in `check.py`, the audit/findings entrypoints, and the fixture builder now declares UTF-8. Generated fixture/manifest text declares UTF-8 and LF.
- Both reference verification paths hash raw on-disk bytes. The reference fetcher writes UTF-8 bytes directly, then hashes those written bytes; it writes the manifest as UTF-8 LF.
- `tests/test_portability.py` adds five offline standard-library regressions. They emulate cp1252 defaults and Windows newline translation, verify Unicode inputs/reports/notices survive unchanged, run all existing gates under that emulation, reject CRLF byte tampering, and mock the W3C fetch into a temporary directory.
- CI retains Ubuntu/Windows/macOS × Python 3.10/3.13, adds `fail-fast: false`, runs unittest discovery before the unchanged custom gates, and requires exact exit 1 for the planted citation rejection.

## Test-first evidence and actual results

The first `python3 -m unittest discover -s tests -v` ran before production edits: four failures and one UnicodeEncodeError. The retained red transcript is below. After the fix, all five regressions pass on local Python 3.14.6 and Python 3.13.14. Both interpreters run the custom gate with 131/131 checks passing and return exact exit 1 for the planted broken report. See the exact version output below for the host versions.

Read-only Git checks confirm a clean whitespace diff, LF attributes, and exact preserved bytes. TEST_METHOD.md is byte-identical to 0b57525; all six normative excerpts and the reference manifest are byte-identical to c6007d4.

## Scope and limitations

Only assigned source/test/workflow files and this task's receipts were written. No Git state mutations, commits, staging, branch changes, subagents, live network fetches, normative text edits, fixture regeneration, or shared planning document edits occurred. The fixture builder's encoding edits were reviewed; its live network/PyYAML generation was not run. Windows defaults are emulated locally, including newline writes; this does not substitute for real Windows/Linux CI. Python 3.10 was unavailable locally. The lead must review, commit/push, and verify all six CI jobs before Task 2.

## Full red output

Command: `python3 -m unittest discover -s tests -v`

```text
test_all_existing_gates_with_windows_default_encoding (test_portability.PortabilityTests.test_all_existing_gates_with_windows_default_encoding) ... FAIL
test_audit_reads_utf8_input (test_portability.PortabilityTests.test_audit_reads_utf8_input) ... FAIL
test_both_reference_gates_reject_changed_line_ending_bytes (test_portability.PortabilityTests.test_both_reference_gates_reject_changed_line_ending_bytes) ... FAIL
test_fetch_writes_utf8_lf_bytes_matching_manifest (test_portability.PortabilityTests.test_fetch_writes_utf8_lf_bytes_matching_manifest) ... ERROR
test_findings_reads_utf8_report_and_notices (test_portability.PortabilityTests.test_findings_reads_utf8_report_and_notices) ... FAIL

======================================================================
ERROR: test_fetch_writes_utf8_lf_bytes_matching_manifest (test_portability.PortabilityTests.test_fetch_writes_utf8_lf_bytes_matching_manifest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/tests/test_portability.py", line 158, in test_fetch_writes_utf8_lf_bytes_matching_manifest
    self.assertEqual(fetch.main(), 0)
                     ~~~~~~~~~~^^
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/auditor/reference/fetch-standard.py", line 109, in main
    out = HERE / f"wcag21-{num}.md"; out.write_text(doc)
                                     ~~~~~~~~~~~~~~^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/pathlib/__init__.py", line 810, in write_text
    return f.write(data)
           ~~~~~~~^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/encodings/cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 167-169: character maps to <undefined>

======================================================================
FAIL: test_all_existing_gates_with_windows_default_encoding (test_portability.PortabilityTests.test_all_existing_gates_with_windows_default_encoding)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/tests/test_portability.py", line 56, in test_all_existing_gates_with_windows_default_encoding
    self.assertEqual(check.main(["check.py"]), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0

======================================================================
FAIL: test_audit_reads_utf8_input (test_portability.PortabilityTests.test_audit_reads_utf8_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/tests/test_portability.py", line 81, in test_audit_reads_utf8_input
    self.assertIn("Copyright © – 日本語", output.getvalue())
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'Copyright © – 日本語' not found in 'WCAG 2.1 Level AA contrast audit\nverdict: PASS\n1 element(s): 1 pass, 0 fail, 0 undecidable, 0 n/a, 0 blocker(s)\n\n[pass] Copyright Â© â€“ æ—¥æœ¬èªž  SC 1.4.3 (AA)\n        21.0:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)\n        provision: reference/wcag21-1.4.3.md\n        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"\n        input: fg=#000 bg=#fff font_px=16.0 bold=false kind=text\n'

======================================================================
FAIL: test_both_reference_gates_reject_changed_line_ending_bytes (test_portability.PortabilityTests.test_both_reference_gates_reject_changed_line_ending_bytes)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/tests/test_portability.py", line 117, in test_both_reference_gates_reject_changed_line_ending_bytes
    self.assertTrue(check.findings.verify_reference(ref))
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: [] is not true

======================================================================
FAIL: test_findings_reads_utf8_report_and_notices (test_portability.PortabilityTests.test_findings_reads_utf8_report_and_notices)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/alexhale/Projects/agents-worktrees/wcag-comp-12-finish/tests/test_portability.py", line 105, in test_findings_reads_utf8_report_and_notices
    self.assertEqual(check.findings.main(), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0

----------------------------------------------------------------------
Ran 5 tests in 0.051s

FAILED (failures=4, errors=1)
```

## Full green output

Command: `python3 -m unittest discover -s tests -v`

```text
test_all_existing_gates_with_windows_default_encoding (test_portability.PortabilityTests.test_all_existing_gates_with_windows_default_encoding) ... ok
test_audit_reads_utf8_input (test_portability.PortabilityTests.test_audit_reads_utf8_input) ... ok
test_both_reference_gates_reject_changed_line_ending_bytes (test_portability.PortabilityTests.test_both_reference_gates_reject_changed_line_ending_bytes) ... ok
test_fetch_writes_utf8_lf_bytes_matching_manifest (test_portability.PortabilityTests.test_fetch_writes_utf8_lf_bytes_matching_manifest) ... ok
test_findings_reads_utf8_report_and_notices (test_portability.PortabilityTests.test_findings_reads_utf8_report_and_notices) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.061s

OK
```

## Full validation commands and output

```text
$ python3 --version
Python 3.14.6
EXIT: 0

$ python3.13 --version
Python 3.13.14
EXIT: 0

$ python3.13 -m unittest discover -s tests -v
test_all_existing_gates_with_windows_default_encoding (test_portability.PortabilityTests.test_all_existing_gates_with_windows_default_encoding) ... ok
test_audit_reads_utf8_input (test_portability.PortabilityTests.test_audit_reads_utf8_input) ... ok
test_both_reference_gates_reject_changed_line_ending_bytes (test_portability.PortabilityTests.test_both_reference_gates_reject_changed_line_ending_bytes) ... ok
test_fetch_writes_utf8_lf_bytes_matching_manifest (test_portability.PortabilityTests.test_fetch_writes_utf8_lf_bytes_matching_manifest) ... ok
test_findings_reads_utf8_report_and_notices (test_portability.PortabilityTests.test_findings_reads_utf8_report_and_notices) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.047s

OK
EXIT: 0

$ python3 check.py

[1] SHAPE: the drop-in folder holds the declared set and nothing else
  ok    auditor/ exists
  ok    auditor/ has every declared item
  ok    auditor/ has nothing undeclared
  ok    exact filename: README.md
  ok    exact filename: checker
  ok    exact filename: examples.md
  ok    exact filename: identity.md
  ok    exact filename: reference
  ok    exact filename: rules.md

[2] PROVENANCE: the cited standard is on disk, dated, hashed, with its status
  ok    auditor/reference/MANIFEST.json exists
  ok    manifest records the retrieval date
  ok    manifest pins a hash of the source document
  ok    manifest records the document status
  ok    1.4.11: wcag21-1.4.11.md exists on disk
  ok    1.4.11: carries the W3C status line
  ok    1.4.11: carries the W3C licence notice
  ok    1.4.11: file hash matches the manifest
  ok    1.4.3: wcag21-1.4.3.md exists on disk
  ok    1.4.3: carries the W3C status line
  ok    1.4.3: carries the W3C licence notice
  ok    1.4.3: file hash matches the manifest
  ok    1.4.6: wcag21-1.4.6.md exists on disk
  ok    1.4.6: carries the W3C status line
  ok    1.4.6: carries the W3C licence notice
  ok    1.4.6: file hash matches the manifest
  ok    contrast-ratio: wcag21-glossary-contrast-ratio.md exists on disk
  ok    contrast-ratio: carries the W3C status line
  ok    contrast-ratio: carries the W3C licence notice
  ok    contrast-ratio: file hash matches the manifest
  ok    large-scale-text: wcag21-glossary-large-scale-text.md exists on disk
  ok    large-scale-text: carries the W3C status line
  ok    large-scale-text: carries the W3C licence notice
  ok    large-scale-text: file hash matches the manifest
  ok    relative-luminance: wcag21-glossary-relative-luminance.md exists on disk
  ok    relative-luminance: carries the W3C status line
  ok    relative-luminance: carries the W3C licence notice
  ok    relative-luminance: file hash matches the manifest
  ok    code cites wcag21-1.4.11.md, which the manifest lists
  ok    code cites wcag21-1.4.3.md, which the manifest lists
  ok    code cites wcag21-1.4.6.md, which the manifest lists
  ok    quote is verbatim in wcag21-1.4.3.md: "Large-scale text and images of large-scale text ..."
  ok    quote is verbatim in wcag21-1.4.6.md: "Large-scale text and images of large-scale text ..."
  ok    quote is verbatim in wcag21-1.4.3.md: "Text or images of text that are part of an inact..."
  ok    quote is verbatim in wcag21-1.4.3.md: "Text that is part of a logo or brand name has no..."
  ok    quote is verbatim in wcag21-1.4.3.md: "The visual presentation of text and images of te..."
  ok    quote is verbatim in wcag21-1.4.6.md: "The visual presentation of text and images of te..."
  ok    quote is verbatim in wcag21-1.4.11.md: "The visual presentation of the following have a ..."
  ok    quote is verbatim in wcag21-1.4.11.md: "Visual information required to identify user int..."
  ok    quote is verbatim in wcag21-1.4.11.md: "except for inactive components or where the appe..."

[3] ANCHOR: ratio math against known boundary values
  ok    #000000 on #ffffff == 21.0:1
  ok    #ffffff on #ffffff == 1.0:1
  ok    #767676 on #ffffff == 4.5:1
  ok    #777777 on #ffffff == 4.4:1
  ok    ratio is symmetric
  ok    rounding never rounds a fail up to the bar
  ok    large text starts at 24px (18pt) regular
  ok    large bold text starts at 18.67px (14pt)

[4] MUTATION: each rule must go red on input built to break it
  ok    1.4.3 normal text below 4.5:1 -> FAIL
  ok    1.4.3 large text below 3:1 -> FAIL
  ok    1.4.11 non-text below 3:1 -> FAIL
  ok    large-text exception actually changes the verdict
  ok    severity separates a near miss from unreadable
  ok    exactly two thirds of the bar is major, not blocker
  ok    just under two thirds is blocker
  ok    font_pt 18 is large text (24px), font_px 18 is not
  ok    font_weight 700 is bold, 600 is not
  ok    font_weight 'bold' and font_px '19px' are read, not crashed on
  ok    an unreadable size is one UNDECIDABLE finding, not a traceback
  ok    8-digit hex with alpha is refused as non-opaque
  ok    8-digit hex with full alpha is measured
  ok    alpha above 1 is refused
  ok    opacity below 1 is refused, not measured
  ok    named logotype is N/A and quotes the Logotypes clause
  ok    the same pair without the exemption named is FAIL
  ok    an exemption the criterion does not have is refused
  ok    a divider named decorative is N/A under 1.4.11 and quotes the 'required to identify' clause
  ok    an undecidable non-text element cites 1.4.11, not 1.4.3

[5] SILENCE: compliant input must produce no AA failures, and passes are reported
  ok    clean fixture returns verdict PASS
  ok    clean fixture invents zero failures
  ok    clean fixture reports every pass
  ok    violating fixture returns verdict FAIL
  ok    an AAA miss is never printed as [FAIL]
  ok    an AAA miss is printed as headroom
  ok    an undecided audit is INCOMPLETE, exit 2, never a silent pass

[6] INVARIANCE: one violation, five spellings, five identical verdicts
  ok    all five spellings produce the same verdict
  ok    all five spellings produce the same ratio
  ok    and that shared verdict is FAIL

[7] PURITY: the deterministic layer reaches nothing outside itself
  ok    auditor/checker/contrast.py imports nothing that reaches out
  ok    auditor/checker/contrast.py has no dynamic import or eval
  ok    auditor/checker/audit.py imports nothing that reaches out
  ok    auditor/checker/audit.py has no dynamic import or eval
  ok    auditor/checker/findings.py imports nothing that reaches out
  ok    auditor/checker/findings.py has no dynamic import or eval

[8] CITATION: every finding names a real provision, quotes it verbatim, and recomputes
  ok    the checker's own output parses back
  ok    the checker's own output passes its own gate
  ok    examples/findings-broken.md parses to four findings
  ok    the valid finding holds

  --- DEMONSTRATION: the citation gate, fired on purpose
      caught: orange CTA text: A_UNKNOWN_SC: SC 1.4.13 is not in reference/MANIFEST.json
      caught: ghost border: C_QUOTE_NOT_VERBATIM: quote is not in reference/wcag21-1.4.11.md
      caught: no size given: D_KIND_MISMATCH: SC 1.4.11 applies to nontext, element is text
      caught: no size given: F_RATIO_MISMATCH: finding says FAIL 4.5:1, checker recomputes ('UNDECIDABLE', 4.5)
      caught: no size given: F_SEVERITY_MISMATCH: finding says major, checker recomputes unknown
  ok    planted nonexistent SC is caught by check A
  ok    planted non-verbatim quote is caught by check C
  ok    planted wrong-kind criterion is caught by check D
  ok    exactly three of four findings rejected
  ok    a real 1.4.3 quote under the 1.4.11 file is rejected (B_FILE_MISMATCH)
  ok    SC 1.4.6 labelled AA over the 1.4.3 file is rejected
  ok    a finding with no input line is rejected (I_NO_INPUT)
  ok    an unknown mark is rejected (H_UNKNOWN_MARK)
  ok    an indented finding is still parsed
  ok    a provision outside reference/ is rejected, never opened
  ok    a wrong severity is rejected (F_SEVERITY_MISMATCH)
  ok    an AAA headroom line with a wrong ratio is recomputed and rejected
  ok    a malformed input line is a rejection, not a crash
  ok    reference files hash to the manifest before any citation is judged

[9] EXAMPLES: every pasted output in examples.md is a live run of the checker
  ok    examples.md carries at least three tagged output blocks
  ok    full output for fixtures/clean.json equals a live run byte for byte
  ok    full output for fixtures/violating.json equals a live run byte for byte
  ok    excerpt of fixtures/violating.json appears verbatim in a live run
  ok    full output for fixtures/exempt.json equals a live run byte for byte

[10] TERRITORY: real public brand token files re-audit to the committed verdicts
  ok    receipts/EXPECTED-brands.json exists
  ok    at least 40 brand fixtures on disk
  ok    every fixture has a committed expectation
  ok    every fixture names a pinned upstream commit, its hash, and matched it at build time
  ok    no fixture drifted from its committed verdicts
      58 brands: FAIL 48, INCOMPLETE 2, PASS 8; 4 undecidable element(s) reported, none skipped
  ok    at least five pairs were hand-anchored against WebAIM
  ok    airbnb muted on canvas: ours 5.4:1 vs WebAIM 5.4:1
  ok    airbnb on-primary on primary: ours 3.5:1 vs WebAIM 3.51:1
  ok    anthropic on-primary on primary: ours 3.2:1 vs WebAIM 3.27:1
  ok    cursor ink on canvas: ours 14.3:1 vs WebAIM 14.3:1
  ok    coinbase muted on canvas: ours 3.8:1 vs WebAIM 3.87:1
  ok    mintlify hairline on canvas: ours 1.2:1 vs WebAIM 1.25:1

[11] DIFFERENTIAL: an independent luminance implementation agrees on every brand pair
  ok    208 opaque pairs compared against the vendored oracle
  ok    zero disagreements beyond 0.01
  ok    every opaque pair carries the oracle's build-time ratio

==============================================================
131 checks in 11 gates: 131 passed, 0 failed
GATE PASSED. What each gate proved is in its own lines above; what a gate
looks like when it fails is in receipts/DEVIATIONS.md.
EXIT: 0

$ python3 check.py examples/findings-broken.md
holds    muted caption  SC 1.4.3 (AA)
REJECTED orange CTA text  SC 1.4.13 (AA)
           A_UNKNOWN_SC: SC 1.4.13 is not in reference/MANIFEST.json
REJECTED ghost border  SC 1.4.11 (AA)
           C_QUOTE_NOT_VERBATIM: quote is not in reference/wcag21-1.4.11.md
REJECTED no size given  SC 1.4.11 (AA)
           D_KIND_MISMATCH: SC 1.4.11 applies to nontext, element is text
           F_RATIO_MISMATCH: finding says FAIL 4.5:1, checker recomputes ('UNDECIDABLE', 4.5)
           F_SEVERITY_MISMATCH: finding says major, checker recomputes unknown

4 citation(s) checked, 3 rejected
EXIT: 1

$ python3.13 check.py

[1] SHAPE: the drop-in folder holds the declared set and nothing else
  ok    auditor/ exists
  ok    auditor/ has every declared item
  ok    auditor/ has nothing undeclared
  ok    exact filename: README.md
  ok    exact filename: checker
  ok    exact filename: examples.md
  ok    exact filename: identity.md
  ok    exact filename: reference
  ok    exact filename: rules.md

[2] PROVENANCE: the cited standard is on disk, dated, hashed, with its status
  ok    auditor/reference/MANIFEST.json exists
  ok    manifest records the retrieval date
  ok    manifest pins a hash of the source document
  ok    manifest records the document status
  ok    1.4.11: wcag21-1.4.11.md exists on disk
  ok    1.4.11: carries the W3C status line
  ok    1.4.11: carries the W3C licence notice
  ok    1.4.11: file hash matches the manifest
  ok    1.4.3: wcag21-1.4.3.md exists on disk
  ok    1.4.3: carries the W3C status line
  ok    1.4.3: carries the W3C licence notice
  ok    1.4.3: file hash matches the manifest
  ok    1.4.6: wcag21-1.4.6.md exists on disk
  ok    1.4.6: carries the W3C status line
  ok    1.4.6: carries the W3C licence notice
  ok    1.4.6: file hash matches the manifest
  ok    contrast-ratio: wcag21-glossary-contrast-ratio.md exists on disk
  ok    contrast-ratio: carries the W3C status line
  ok    contrast-ratio: carries the W3C licence notice
  ok    contrast-ratio: file hash matches the manifest
  ok    large-scale-text: wcag21-glossary-large-scale-text.md exists on disk
  ok    large-scale-text: carries the W3C status line
  ok    large-scale-text: carries the W3C licence notice
  ok    large-scale-text: file hash matches the manifest
  ok    relative-luminance: wcag21-glossary-relative-luminance.md exists on disk
  ok    relative-luminance: carries the W3C status line
  ok    relative-luminance: carries the W3C licence notice
  ok    relative-luminance: file hash matches the manifest
  ok    code cites wcag21-1.4.11.md, which the manifest lists
  ok    code cites wcag21-1.4.3.md, which the manifest lists
  ok    code cites wcag21-1.4.6.md, which the manifest lists
  ok    quote is verbatim in wcag21-1.4.3.md: "Large-scale text and images of large-scale text ..."
  ok    quote is verbatim in wcag21-1.4.6.md: "Large-scale text and images of large-scale text ..."
  ok    quote is verbatim in wcag21-1.4.3.md: "Text or images of text that are part of an inact..."
  ok    quote is verbatim in wcag21-1.4.3.md: "Text that is part of a logo or brand name has no..."
  ok    quote is verbatim in wcag21-1.4.3.md: "The visual presentation of text and images of te..."
  ok    quote is verbatim in wcag21-1.4.6.md: "The visual presentation of text and images of te..."
  ok    quote is verbatim in wcag21-1.4.11.md: "The visual presentation of the following have a ..."
  ok    quote is verbatim in wcag21-1.4.11.md: "Visual information required to identify user int..."
  ok    quote is verbatim in wcag21-1.4.11.md: "except for inactive components or where the appe..."

[3] ANCHOR: ratio math against known boundary values
  ok    #000000 on #ffffff == 21.0:1
  ok    #ffffff on #ffffff == 1.0:1
  ok    #767676 on #ffffff == 4.5:1
  ok    #777777 on #ffffff == 4.4:1
  ok    ratio is symmetric
  ok    rounding never rounds a fail up to the bar
  ok    large text starts at 24px (18pt) regular
  ok    large bold text starts at 18.67px (14pt)

[4] MUTATION: each rule must go red on input built to break it
  ok    1.4.3 normal text below 4.5:1 -> FAIL
  ok    1.4.3 large text below 3:1 -> FAIL
  ok    1.4.11 non-text below 3:1 -> FAIL
  ok    large-text exception actually changes the verdict
  ok    severity separates a near miss from unreadable
  ok    exactly two thirds of the bar is major, not blocker
  ok    just under two thirds is blocker
  ok    font_pt 18 is large text (24px), font_px 18 is not
  ok    font_weight 700 is bold, 600 is not
  ok    font_weight 'bold' and font_px '19px' are read, not crashed on
  ok    an unreadable size is one UNDECIDABLE finding, not a traceback
  ok    8-digit hex with alpha is refused as non-opaque
  ok    8-digit hex with full alpha is measured
  ok    alpha above 1 is refused
  ok    opacity below 1 is refused, not measured
  ok    named logotype is N/A and quotes the Logotypes clause
  ok    the same pair without the exemption named is FAIL
  ok    an exemption the criterion does not have is refused
  ok    a divider named decorative is N/A under 1.4.11 and quotes the 'required to identify' clause
  ok    an undecidable non-text element cites 1.4.11, not 1.4.3

[5] SILENCE: compliant input must produce no AA failures, and passes are reported
  ok    clean fixture returns verdict PASS
  ok    clean fixture invents zero failures
  ok    clean fixture reports every pass
  ok    violating fixture returns verdict FAIL
  ok    an AAA miss is never printed as [FAIL]
  ok    an AAA miss is printed as headroom
  ok    an undecided audit is INCOMPLETE, exit 2, never a silent pass

[6] INVARIANCE: one violation, five spellings, five identical verdicts
  ok    all five spellings produce the same verdict
  ok    all five spellings produce the same ratio
  ok    and that shared verdict is FAIL

[7] PURITY: the deterministic layer reaches nothing outside itself
  ok    auditor/checker/contrast.py imports nothing that reaches out
  ok    auditor/checker/contrast.py has no dynamic import or eval
  ok    auditor/checker/audit.py imports nothing that reaches out
  ok    auditor/checker/audit.py has no dynamic import or eval
  ok    auditor/checker/findings.py imports nothing that reaches out
  ok    auditor/checker/findings.py has no dynamic import or eval

[8] CITATION: every finding names a real provision, quotes it verbatim, and recomputes
  ok    the checker's own output parses back
  ok    the checker's own output passes its own gate
  ok    examples/findings-broken.md parses to four findings
  ok    the valid finding holds

  --- DEMONSTRATION: the citation gate, fired on purpose
      caught: orange CTA text: A_UNKNOWN_SC: SC 1.4.13 is not in reference/MANIFEST.json
      caught: ghost border: C_QUOTE_NOT_VERBATIM: quote is not in reference/wcag21-1.4.11.md
      caught: no size given: D_KIND_MISMATCH: SC 1.4.11 applies to nontext, element is text
      caught: no size given: F_RATIO_MISMATCH: finding says FAIL 4.5:1, checker recomputes ('UNDECIDABLE', 4.5)
      caught: no size given: F_SEVERITY_MISMATCH: finding says major, checker recomputes unknown
  ok    planted nonexistent SC is caught by check A
  ok    planted non-verbatim quote is caught by check C
  ok    planted wrong-kind criterion is caught by check D
  ok    exactly three of four findings rejected
  ok    a real 1.4.3 quote under the 1.4.11 file is rejected (B_FILE_MISMATCH)
  ok    SC 1.4.6 labelled AA over the 1.4.3 file is rejected
  ok    a finding with no input line is rejected (I_NO_INPUT)
  ok    an unknown mark is rejected (H_UNKNOWN_MARK)
  ok    an indented finding is still parsed
  ok    a provision outside reference/ is rejected, never opened
  ok    a wrong severity is rejected (F_SEVERITY_MISMATCH)
  ok    an AAA headroom line with a wrong ratio is recomputed and rejected
  ok    a malformed input line is a rejection, not a crash
  ok    reference files hash to the manifest before any citation is judged

[9] EXAMPLES: every pasted output in examples.md is a live run of the checker
  ok    examples.md carries at least three tagged output blocks
  ok    full output for fixtures/clean.json equals a live run byte for byte
  ok    full output for fixtures/violating.json equals a live run byte for byte
  ok    excerpt of fixtures/violating.json appears verbatim in a live run
  ok    full output for fixtures/exempt.json equals a live run byte for byte

[10] TERRITORY: real public brand token files re-audit to the committed verdicts
  ok    receipts/EXPECTED-brands.json exists
  ok    at least 40 brand fixtures on disk
  ok    every fixture has a committed expectation
  ok    every fixture names a pinned upstream commit, its hash, and matched it at build time
  ok    no fixture drifted from its committed verdicts
      58 brands: FAIL 48, INCOMPLETE 2, PASS 8; 4 undecidable element(s) reported, none skipped
  ok    at least five pairs were hand-anchored against WebAIM
  ok    airbnb muted on canvas: ours 5.4:1 vs WebAIM 5.4:1
  ok    airbnb on-primary on primary: ours 3.5:1 vs WebAIM 3.51:1
  ok    anthropic on-primary on primary: ours 3.2:1 vs WebAIM 3.27:1
  ok    cursor ink on canvas: ours 14.3:1 vs WebAIM 14.3:1
  ok    coinbase muted on canvas: ours 3.8:1 vs WebAIM 3.87:1
  ok    mintlify hairline on canvas: ours 1.2:1 vs WebAIM 1.25:1

[11] DIFFERENTIAL: an independent luminance implementation agrees on every brand pair
  ok    208 opaque pairs compared against the vendored oracle
  ok    zero disagreements beyond 0.01
  ok    every opaque pair carries the oracle's build-time ratio

==============================================================
131 checks in 11 gates: 131 passed, 0 failed
GATE PASSED. What each gate proved is in its own lines above; what a gate
looks like when it fails is in receipts/DEVIATIONS.md.
EXIT: 0

$ python3.13 check.py examples/findings-broken.md
holds    muted caption  SC 1.4.3 (AA)
REJECTED orange CTA text  SC 1.4.13 (AA)
           A_UNKNOWN_SC: SC 1.4.13 is not in reference/MANIFEST.json
REJECTED ghost border  SC 1.4.11 (AA)
           C_QUOTE_NOT_VERBATIM: quote is not in reference/wcag21-1.4.11.md
REJECTED no size given  SC 1.4.11 (AA)
           D_KIND_MISMATCH: SC 1.4.11 applies to nontext, element is text
           F_RATIO_MISMATCH: finding says FAIL 4.5:1, checker recomputes ('UNDECIDABLE', 4.5)
           F_SEVERITY_MISMATCH: finding says major, checker recomputes unknown

4 citation(s) checked, 3 rejected
EXIT: 1

$ git diff --check
EXIT: 0

$ git diff --exit-code c6007d4 -- TEST_METHOD.md auditor/reference/*.md auditor/reference/MANIFEST.json
EXIT: 0

$ git check-attr text eol -- auditor/reference/wcag21-1.4.3.md TEST_METHOD.md fixtures/clean.json
auditor/reference/wcag21-1.4.3.md: text: auto
auditor/reference/wcag21-1.4.3.md: eol: lf
TEST_METHOD.md: text: auto
TEST_METHOD.md: eol: lf
fixtures/clean.json: text: auto
fixtures/clean.json: eol: lf
EXIT: 0
```

## Byte preservation evidence

Compared `git show <commit>:<path>` bytes directly with `Path(path).read_bytes()`; all comparisons passed.

```text
TEST_METHOD.md: byte-identical to 0b57525; SHA-256 6f62a872180d4361c50089c3db786b51214a22cf500e0d0210f877ae934b3c41
auditor/reference/wcag21-1.4.11.md: byte-identical to c6007d4; SHA-256 62b56dd0e9f54d69d1924097363b62728ff310e75f25516a5ef7673633ad5e52
auditor/reference/wcag21-1.4.3.md: byte-identical to c6007d4; SHA-256 e4b0c19572283c6565a076fa0ff93c817cd304781c1f3b6c7f29576a8fa1563d
auditor/reference/wcag21-1.4.6.md: byte-identical to c6007d4; SHA-256 54a1c1e99f27c9d9779c303771ae9ad0ad5cd5fd785d90655185fbfd25a04df7
auditor/reference/wcag21-glossary-contrast-ratio.md: byte-identical to c6007d4; SHA-256 d06296be9d7ca1d2bacd3b61f8f8b335b5e0bbd760a828cdb6ea8015c34fa3f1
auditor/reference/wcag21-glossary-large-scale-text.md: byte-identical to c6007d4; SHA-256 5f3a5a32dd7327bce7c029e591a0699389b6aa4f97e7dd6a6c1e0fa7a80a1e95
auditor/reference/wcag21-glossary-relative-luminance.md: byte-identical to c6007d4; SHA-256 2873f80656c12b344ab70600df5882a7d56766b0bc8352cb7e1bb63c28e3a0f7
auditor/reference/MANIFEST.json: byte-identical to c6007d4; SHA-256 00c470fd144a0723621429ede1c0c564bfa555fa654a65b7ce78a8c3a186d758
```
