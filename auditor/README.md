# WCAG 2.1 contrast auditor

Checks colour pairs against three success criteria of the W3C Web Content
Accessibility Guidelines 2.1 and reports what passes, what fails, where, by how
much, and which provision says so. Drop this folder into a Claude project and
Claude becomes the auditor. Or run the checker yourself; it is the same number.

## Use it in three steps

1. Write the colour pairs you want checked as a JSON list. One entry per
   foreground-on-background pair:

   ```json
   [
     {"id": "body copy",    "fg": "#1a1a1a", "bg": "#ffffff", "font_px": 16, "kind": "text"},
     {"id": "h1",           "fg": "#0d4a6b", "bg": "#ffffff", "font_px": 40, "bold": true, "kind": "text"},
     {"id": "input border", "fg": "#5a5a5a", "bg": "#ffffff", "kind": "nontext"}
   ]
   ```

   `kind` is `text` or `nontext`. Text needs a size (`font_px` or `font_pt`) because
   the standard sets a lower bar for large text. `bold` or `font_weight` matters for
   the same reason. Colours may be `#rgb`, `#rrggbb`, `rgb()`, opaque `rgba()`, or
   a common name. Anything with transparency is refused, not guessed.

2. Run the checker from inside this folder:

   ```bash
   python3 checker/audit.py your-pairs.json
   ```

3. Read the report. Every finding has six parts: where, which criterion, the
   measured ratio against the required one, the file in `reference/` the rule
   came from, the rule quoted from that file, and the input that was measured.

   ```text
   [FAIL] muted caption  SC 1.4.3 (AA)  severity=blocker
           2.8:1 against a 4.5:1 minimum for text under 18pt, or under 14pt bold (measured at 13px)
           provision: reference/wcag21-1.4.3.md
           quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
           input: fg=#999999 bg=#ffffff font_px=13.0 bold=false kind=text
   ```

   Exit code 0 means every AA criterion passed. 1 means at least one failed.
   2 means something could not be measured, and the report says what.

## What it will and will not do

It enforces 1.4.3 Contrast (Minimum) and 1.4.11 Non-text Contrast at Level AA,
and reports 1.4.6 Contrast (Enhanced) as AAA headroom, never as a failure. The
text of all three, and the definitions the math comes from, sit in `reference/`
with the W3C licence, the document status, and a hash.

It never estimates. If a colour is transparent, a size is missing, or a format is
unknown, the finding says UNDECIDABLE and the audit is INCOMPLETE. It does not
decide that text is a logo; if you mark an element `"exempt": "logotype"` it
reports N/A and quotes the exception clause. It has no opinion about whether a
colour is nice.

Alt text, focus order, headings, motion and the other 75 criteria are out of
scope, and it says so instead of guessing.

## If you are Claude

Read `identity.md`, then `rules.md`. Extract the pairs, write the JSON, run the
checker if you can execute code. If you cannot, every ratio is UNDECIDABLE and
you say so; you still cite the criterion and quote the provision. Four worked
audits are in `examples.md`, each one a real run.

## Files

- `identity.md` who the auditor is and what it refuses to do
- `rules.md` audit order, the six-part finding, severity, the two measuring modes
- `examples.md` four real runs, including one it refuses to decide and one the standard exempts
- `reference/` WCAG 2.1 SC 1.4.3, 1.4.11, 1.4.6 and three glossary definitions, verbatim
- `checker/` the ratio math (`contrast.py`), the findings (`audit.py`), the citation gate (`findings.py`)
