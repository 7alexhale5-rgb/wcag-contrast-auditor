# Examples

Four worked audits. Every block below is tagged with the fixture it came from, and
`check.py` re-runs that fixture and refuses to pass unless the block equals the
live output. Nothing here was edited by hand.

## 1. A page that passes

Input: `fixtures/clean.json`. Body copy, a heading, a primary button, an input border.

```text fixture=fixtures/clean.json
WCAG 2.1 Level AA contrast audit
verdict: PASS
4 element(s): 4 pass, 0 fail, 0 undecidable, 0 n/a, 0 blocker(s)

[pass] body copy  SC 1.4.3 (AA)
        17.4:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#1a1a1a bg=#ffffff font_px=16.0 bold=false kind=text
[pass] h1  SC 1.4.3 (AA)
        9.5:1 against a 3.0:1 minimum for large text: 18pt+, or 14pt+ bold (measured at 40px, bold)
        provision: reference/wcag21-1.4.3.md
        quote: "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1"
        input: fg=#0d4a6b bg=#ffffff font_px=40.0 bold=true kind=text
[pass] primary button  SC 1.4.3 (AA)
        9.5:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#ffffff bg=#0d4a6b font_px=16.0 bold=false kind=text
[pass] input border  SC 1.4.11 (AA)
        6.8:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
        quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s)"
        input: fg=#5a5a5a bg=#ffffff bold=false kind=nontext
```

Note the heading is measured against 3:1, not 4.5:1. At 40px bold it meets the
large-text exception in 1.4.3, and the report says so rather than leaving the
reader to work out which threshold was applied. Every finding carries the
provision file, the requirement quoted from it, and the input it measured, so a
reader can open the file and recompute the number.

## 2. A page that fails

Input: `fixtures/violating.json`.

```text fixture=fixtures/violating.json
WCAG 2.1 Level AA contrast audit
verdict: FAIL
4 element(s): 0 pass, 3 fail, 1 undecidable, 0 n/a, 3 blocker(s)

[FAIL] muted caption  SC 1.4.3 (AA)  severity=blocker
        2.8:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 13px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#999999 bg=#ffffff font_px=13.0 bold=false kind=text
[aaa ] muted caption  SC 1.4.6 (AAA)
        AAA headroom: 2.8:1 against 7.0:1. Not required for AA.
        provision: reference/wcag21-1.4.6.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 7:1"
        input: fg=#999999 bg=#ffffff font_px=13.0 bold=false kind=text
[FAIL] orange CTA text  SC 1.4.3 (AA)  severity=blocker
        2.7:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#f47b20 bg=#ffffff font_px=16.0 bold=false kind=text
[aaa ] orange CTA text  SC 1.4.6 (AAA)
        AAA headroom: 2.7:1 against 7.0:1. Not required for AA.
        provision: reference/wcag21-1.4.6.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 7:1"
        input: fg=#f47b20 bg=#ffffff font_px=16.0 bold=false kind=text
[FAIL] ghost border  SC 1.4.11 (AA)  severity=blocker
        1.2:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
        quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s)"
        input: fg=#e8e8e8 bg=#ffffff bold=false kind=nontext
[????] no size given  SC 1.4.3 (AA)
        measured 4.5:1 but no font size given, so the large-text exception cannot be resolved
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#767676 bg=#ffffff bold=false kind=text
```

Every line carries a location, a criterion, a measured number against a required
number, and a file you can open. None of it is a judgement about the design. The
`[aaa ]` lines are headroom: a miss against 1.4.6 is never a failure at Level AA,
and printing it as one would misstate the standard.

## 3. The one it refuses to decide

The fourth element in that fixture is `#767676` on white with no font size.

```text excerpt fixture=fixtures/violating.json
[????] no size given  SC 1.4.3 (AA)
        measured 4.5:1 but no font size given, so the large-text exception cannot be resolved
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#767676 bg=#ffffff bold=false kind=text
```

This is the interesting case. 4.5:1 is exactly the AA bar for normal text, so a
lazy auditor reports PASS and moves on. But 1.4.3 sets a different threshold for
large text, and without the font size there is no way to know which rule applies.
The honest answer is that the input did not carry enough information to say. The
overall verdict becomes INCOMPLETE rather than PASS, and the exit code is 2, so a
pipeline cannot mistake it for a pass.

## 4. The one the standard exempts

Input: `fixtures/exempt.json`. A wordmark, named as a logotype by the person who
extracted it. The auditor never decides on its own that text is a logo.

```text fixture=fixtures/exempt.json
WCAG 2.1 Level AA contrast audit
verdict: PASS
1 element(s): 0 pass, 0 fail, 0 undecidable, 1 n/a, 0 blocker(s)

[n/a ] wordmark in header  SC 1.4.3 (AA)
        exempt as logotype: no contrast requirement applies
        provision: reference/wcag21-1.4.3.md
        quote: "Text that is part of a logo or brand name has no contrast requirement."
        input: fg=#e6e6e6 bg=#ffffff font_px=22.0 bold=false exempt=logotype kind=text
```

The verdict is N/A and the quote is the Logotypes clause itself, so an exemption
is as checkable as a failure. Drop the `exempt` field and the same pair is a FAIL.

## What a finding is not

These are all rejected by `rules.md`:

- "The contrast here looks a bit low." No measurement, no criterion.
- "Accessibility issues present on this page." No location.
- "Fails WCAG." No criterion number, so nothing to open and check.
- "Roughly 4.4:1, so probably fine." Two hedges and a wrong conclusion.
