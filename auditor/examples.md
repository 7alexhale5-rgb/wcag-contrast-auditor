# Examples

Three worked audits. All three are real runs of `checker/audit.py`, pasted
unedited. The third is the one that matters most.

## 1. A page that passes

Input, `fixtures/clean.json`: body copy, a heading, a primary button,
an input border.

```
WCAG 2.1 Level AA contrast audit
verdict: PASS
4 element(s): 4 pass, 0 fail, 0 undecidable, 0 blocker(s)

[pass] body copy  SC 1.4.3 (AA)
        17.4:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
[pass] h1  SC 1.4.3 (AA)
        9.5:1 against a 3.0:1 minimum for large text: 18pt+, or 14pt+ bold (measured at 40px, bold)
        provision: reference/wcag21-1.4.3.md
[pass] input border  SC 1.4.11 (AA)
        6.8:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
```

Note the heading is measured against 3:1, not 4.5:1. At 40px bold it meets the
large-text exception in 1.4.3, and the report says so rather than leaving the
reader to work out which threshold was applied.

## 2. A page that fails

Input, `fixtures/violating.json`.

```
verdict: FAIL
4 element(s): 0 pass, 3 fail, 1 undecidable, 3 blocker(s)

[FAIL] muted caption  SC 1.4.3 (AA)  severity=blocker
        2.8:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 13px)
        provision: reference/wcag21-1.4.3.md
[FAIL] orange CTA text  SC 1.4.3 (AA)  severity=blocker
        2.7:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
[FAIL] ghost border  SC 1.4.11 (AA)  severity=blocker
        1.2:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
```

Every line carries a location, a criterion, a measured number against a required
number, and a file you can open. None of it is a judgement about the design.

## 3. The one it refuses to decide

The fourth element in that same fixture is `#767676` on white with no font size.

```
[????] no size given  SC 1.4.3 (AA)
        measured 4.5:1 but no font size given, so the large-text exception
        cannot be resolved
        provision: reference/wcag21-1.4.3.md
```

This is the interesting case. 4.5:1 is exactly the AA bar for normal text, so a
lazy auditor reports PASS and moves on. But 1.4.3 sets a different threshold for
large text, and without the font size there is no way to know which rule applies.
The pair passes under one reading and passes with no margin under the other, and
the honest answer is that the input did not carry enough information to say.

The overall verdict becomes INCOMPLETE rather than PASS when this happens. A gap
you can see beats a number you cannot trust.

## What a finding is not

These are all rejected by `rules.md`:

- "The contrast here looks a bit low." No measurement, no criterion.
- "Accessibility issues present on this page." No location.
- "Fails WCAG." No criterion number, so nothing to open and check.
- "Roughly 4.4:1, so probably fine." Two hedges and a wrong conclusion.
