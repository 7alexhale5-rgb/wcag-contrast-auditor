# Task 2 report: strict inputs and numeric correctness

Original review base: `3bb1958`; round 2 review base: `1046d94`. Source frozen after the REVIEW ROUND 2 FINAL VALIDATION block in `task-2-green.txt`.

## Changes

- `auditor/checker/audit.py`: only normalization and related refusal paths changed. Explicit bold values must be booleans. Font sizes must be finite positive numbers, or numeric strings with the correct field-specific unit. Dual point/pixel and bold/weight declarations must agree. Point conversion no longer rounds to four decimals. Exact rational comparisons against original size values choose the large-text threshold and reject conflicting high-precision dual declarations. Opacity must be finite and within 0..1; only exact opacity 1 is measurable. Invalid source dictionaries remain intact in the finding input instead of being replaced by a kind-only dictionary.
- `auditor/checker/contrast.py`: fractional RGB channels survive parsing. Separate comma/space patterns refuse malformed separators; invalid numbers, nonfinite/out-of-range channels, alpha and extreme exponents raise ColorError. Decimal comparisons prevent almost-one alpha and just-outside-range strings rounding into valid values. Absolute weights must be within 1..1000, preserve the exact 700 boundary, and reject relative bolder/lighter without inherited context. Large-text pixel thresholds align with unrounded point conversion.
- `tests/test_inputs.py`: 17 regression methods cover actual types, nulls, booleans, units, conflicting/equivalent declarations, weight limits, exact and adjacent 14pt/18pt boundaries, opacity bounds and precision, malformed elements mixed with valid inputs, exit precedence and AAA markers, fractional RGB near both AA thresholds, and named errors for malformed colors.
- No check.py assertions needed replacement: the existing 131 checks still pass unchanged.

## Test-first evidence

Full commands, exit statuses, stdout and stderr are preserved in the adjacent `task-2-red.txt` and `task-2-green.txt` files. No failing attempt was removed.

1. Before production changes: 14 test methods, 75 failed subcases and 9 errors.
2. Additional precision/exponent regressions before their fixes: 2 failures and 2 errors. These expose opacity strings `0.999999999999999999999` and `1.000000000000000000001`, plus RGB/alpha Decimal exponent exceptions.
3. Additional exact-weight/tiny-opacity regressions before their fixes: 3 failures and 1 error. These expose numeric weight strings just below 1, above 1000 and below 700, plus an opacity exponent outside Decimal's representation.
4. Review round 1 exposed four size-precision defects: 14pt-bold, 18pt-regular and 24px-regular decimal strings infinitesimally below the threshold rounded up to large-text PASS; a pixel string above 24 falsely agreed with 18pt. Four regressions failed before repair.
5. A conservative precision-refusal intermediate repair passed those initial assertions. The lead ruled that valid precise sizes must receive the actual small-text FAIL, so three revised assertions failed before replacing refusal with exact source-size comparisons. Both attempts remain in the logs; the precision-refusal approach is superseded.

## Review round 2: oversized numeric strings

The reviewer identified finite strings containing over 5000 digits that float parsing accepts but Fraction cannot represent under the runtime's integer-string limit. The error escaped the later threshold path; dual declarations could also leak it during normalization. Two new regression methods cover both leading-zero and trailing-zero forms across pixel, point, and dual inputs, plus mixed CLI input containing a valid AA failure and pass. Before the repair, the targeted run had 6 failures and 8 errors; its complete output is appended to the red log.

The repair only names Fraction ValueError as ColorError and validates exact-size representability during numeric normalization, within the existing per-element error boundary. An oversized element becomes UNDECIDABLE and preserves its original input; the mixed CLI audit still reports its valid AA failure and exits 1. The global integer digit limit is unchanged. No arbitrary-precision parser or other source files were added. Round 1's exact boundary regressions remain green.

## Final verification

All commands returned exit 0 on local Python 3.14.6:

- `python3 -m unittest discover -s tests -p test_inputs.py -v`: 17 passed.
- `python3 -m unittest discover -s tests -v`: 22 passed, including the existing five portability tests.
- `python3 check.py`: 131 checks across 11 gates passed.
- `git diff --check`: clean.

The existing gates verified unchanged example output and brand verdict expectations: 58 fixtures, 48 FAIL, 2 INCOMPLETE, 8 PASS, with 4 undecidable elements. The differential gate compared 208 opaque pairs with no disagreements beyond 0.01. No fixture, expected result or historical receipt was rewritten.

TEST_METHOD.md was compared directly with `git show 0b57525:TEST_METHOD.md` and remains byte-identical (SHA256 `6f62a872180d4361c50089c3db786b51214a22cf500e0d0210f877ae934b3c41`).

## Scope and limitations

Only the two assigned runtime files, the new regression file, and these task receipts were written. Standard library only. No Git mutations, subagents, sends, frozen-method changes, parser edits, or fixture regeneration occurred. The lead owns commit, review and new CI proof; this report claims only local results.

Task 3 still owns typed/lossless rendering and source-bound validation. Retaining raw invalid dictionaries here supplies that later work with the original values; the existing legacy report string remains lossy and is not claimed repaired. Valid normalized findings retain the existing machine format. Review round 1 uses original raw size values locally to classify precise sizes. Their numeric presentation fields can still round; Task 3 must preserve the complete original source in the rendered/typed input so citation recomputation receives the same precision. That parser interface remains deliberately out of scope here.

The three reviewer below-threshold cases now produce AA FAIL with measured 3.5 and required 4.5, with JSON-serializable findings. The conflicting high-precision dual declaration produces UNDECIDABLE. Normal 14pt, numeric 56/3px with 14pt, and the equivalent strings 19.2px/14.4pt remain accepted. Exact comparison adds one private Fraction helper and local source-size threshold selection; no arbitrary-precision channel computation was added.

## Plain-English Summary

### What we're building

A color checker that refuses bad inputs and keeps exact color values.

### Why this piece

Bad inputs could make a failed color pair look safe.

### The surprise

Rounding could turn a faint color into a fully solid one.

### The real problem I caught

False text values could count as bold and lower the passing bar.

### Where we are right now

All local tests pass. Existing sample results stayed the same.

### The one thing left

Review this change, then repair how reports preserve and prove each input.
