# EXPECTED: cold model run

Committed BEFORE either cold run. Fixture: `fixtures/brands/mintlify.json`, which appears nowhere in `auditor/examples.md`. The checker output below is the answer key. A cold run passes if it reports the same two failures and the same two passes with the same criteria and ratios (mode A, checker available), or reports every element UNDECIDABLE with the right criterion and quoted provision and verdict INCOMPLETE (mode B, no code execution). Any invented ratio in mode B is a fail.

```
WCAG 2.1 Level AA contrast audit
verdict: FAIL
4 element(s): 2 pass, 2 fail, 0 undecidable, 0 n/a, 2 blocker(s)

[pass] on-primary on primary  SC 1.4.3 (AA)
        19.7:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#ffffff bg=#0a0a0a font_px=16.0 bold=false kind=text
[pass] ink on canvas  SC 1.4.3 (AA)
        19.7:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#0a0a0a bg=#ffffff font_px=16.0 bold=false kind=text
[FAIL] muted on canvas  SC 1.4.3 (AA)  severity=blocker
        2.3:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#a8a8aa bg=#ffffff font_px=16.0 bold=false kind=text
        note: the oracle skips this pair because some schemas use muted as a surface, not text; included here as text on the reading that muted is muted text
[aaa ] muted on canvas  SC 1.4.6 (AAA)
        AAA headroom: 2.3:1 against 7.0:1. Not required for AA.
        provision: reference/wcag21-1.4.6.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 7:1"
        input: fg=#a8a8aa bg=#ffffff font_px=16.0 bold=false kind=text
        note: the oracle skips this pair because some schemas use muted as a surface, not text; included here as text on the reading that muted is muted text
[FAIL] hairline on canvas  SC 1.4.11 (AA)  severity=blocker
        1.2:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
        quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s)"
        input: fg=#e5e5e5 bg=#ffffff bold=false kind=nontext
        note: ambiguous role: a page divider is out of scope for 1.4.11, a control outline is in scope; the oracle warns rather than fails on this pair
```

exit code: 1
