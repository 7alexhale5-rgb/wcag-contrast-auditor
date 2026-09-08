# RECEIPT: clean clone

Date: 2026-09-08. Cloned from GitHub into an empty temp directory at commit 43d5650 (the commit that carried the territory gate), not from the working copy. Commands and their output, unedited.

```
$ git clone https://github.com/7alexhale5-rgb/wcag-contrast-auditor.git && cd wcag-contrast-auditor
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

...
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
  ok    planted nonexistent SC is caught by check A
  ok    planted non-verbatim quote is caught by check C
  ok    planted wrong-kind criterion is caught by check D
  ok    exactly three of four findings rejected

...
==============================================================
114 checks in 11 gates: 114 passed, 0 failed
GATE PASSED: every rule was shown to fail on purpose, stay quiet on compliant
input, hold across five spellings, cite only what is on disk, and recompute.
exit=0

$ python3 auditor/checker/audit.py fixtures/clean.json; echo exit=$?
exit=0
$ python3 auditor/checker/audit.py fixtures/violating.json; echo exit=$?
exit=1
$ python3 check.py examples/findings-broken.md | tail -1
4 citation(s) checked, 3 rejected
```

No API key. No network at any point after the clone. Python 3 standard library only. The full gate output is 114 lines; it is reproduced in full by running the command.

## Machines that are not mine

GitHub Actions runs `python3 check.py` on every push, on ubuntu, windows and macos, with Python 3.10 and 3.13, and separately asserts that `python3 check.py examples/findings-broken.md` exits non-zero. First run, commit 0f401c5, 2026-09-08 17:14 UTC: conclusion `success`, six of six jobs. Run id 34255886224, readable at https://github.com/7alexhale5-rgb/wcag-contrast-auditor/actions/runs/34255886224 .

```
$ gh run view 34255886224 --json conclusion,headSha
conclusion=success sha=0f401c5
```
