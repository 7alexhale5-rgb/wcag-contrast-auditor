# A findings report that is wrong on purpose

This file ships so that a bare `python3 check.py` fires on the first try and a
reader sees the citation gate working without editing anything. It is a report
against `fixtures/violating.json` in the exact shape `auditor/checker/audit.py`
prints. One finding is valid. Three are planted, one per check the gate makes.

Plant your own: change any `SC` number, `quote:` line, or `input:` kind below,
run `python3 auditor/checker/findings.py examples/findings-broken.md`, and watch
it name the line.

```
[FAIL] muted caption  SC 1.4.3 (AA)  severity=blocker
        2.8:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 13px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#999999 bg=#ffffff font_px=13.0 bold=false kind=text
[FAIL] orange CTA text  SC 1.4.13 (AA)  severity=blocker
        2.7:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 16px)
        provision: reference/wcag21-1.4.3.md
        quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
        input: fg=#f47b20 bg=#ffffff font_px=16.0 bold=false kind=text
[FAIL] ghost border  SC 1.4.11 (AA)  severity=blocker
        1.2:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
        quote: "have a contrast ratio of at least 4.5:1 against adjacent color(s)"
        input: fg=#e8e8e8 bg=#ffffff bold=false kind=nontext
[FAIL] no size given  SC 1.4.11 (AA)  severity=major
        4.5:1 against a 3.0:1 minimum for user interface components and graphical objects
        provision: reference/wcag21-1.4.11.md
        quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s)"
        input: fg=#767676 bg=#ffffff bold=false kind=text
```

- `muted caption`: valid. The gate must accept it.
- `orange CTA text`: cites SC 1.4.13, which does not exist in `reference/`. Check A.
- `ghost border`: quotes a 4.5:1 requirement that is not in the 1.4.11 text. Check C.
- `no size given`: a text element cited under 1.4.11, the non-text criterion. Check D.
