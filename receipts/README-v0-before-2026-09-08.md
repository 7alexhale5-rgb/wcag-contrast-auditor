# WCAG 2.1 Contrast Auditor

A folder-based auditor that checks colour contrast against WCAG 2.1 and reports
what passes, what fails, where exactly, and which provision it violated.

Drop the folder into a Claude project. Claude becomes the auditor.

## What it enforces

Three success criteria from the W3C Web Content Accessibility Guidelines 2.1:
**1.4.3 Contrast (Minimum)** and **1.4.11 Non-text Contrast** at Level AA, plus
**1.4.6 Contrast (Enhanced)** reported as AAA headroom.

The text of all three is in `reference/`, taken from w3.org, with the retrieval
date and a SHA-256 of the source document. You can open any finding, open the
provision it cites, and check that the two agree.

## Feed it

A JSON list of elements. One entry per foreground-on-background pair.

```json
[
  {"id": "body copy",    "fg": "#1a1a1a", "bg": "#ffffff", "font_px": 16, "kind": "text"},
  {"id": "h1",           "fg": "#0d4a6b", "bg": "#ffffff", "font_px": 40, "bold": true, "kind": "text"},
  {"id": "input border", "fg": "#5a5a5a", "bg": "#ffffff", "kind": "nontext"}
]
```

`fg` and `bg` accept `#rgb`, `#rrggbb`, `rgb()`, opaque `rgba()`, or a CSS colour
name. `kind` is `text` or `nontext`. `font_px` and `bold` are required for text,
because 1.4.3 sets a different threshold for large text.

## Run it

```bash
python3 auditor/checker/audit.py your-elements.json          # readable report
python3 auditor/checker/audit.py your-elements.json --json   # full report as JSON
```

Exit code is 1 when any Level AA criterion fails, so it drops into CI unchanged.

## Verify it

This is the part that matters. Run the auditor against itself:

```bash
python3 check.py
```

27 checks across six classes. It proves the ratio math matches values W3C
publishes, that every rule goes red on input built to break it, that compliant
input produces zero findings, that one violation written five different ways
produces five identical verdicts, that the deterministic layer imports nothing
that could reach a network or a model, and that every provision this auditor
cites is actually on disk.

A gate that has only ever run green has proved nothing. This one has been shown
to fail.

## Refresh the standard

```bash
python3 reference/fetch-standard.py && git diff reference/
```

Re-derives `reference/` from w3.org. A clean diff means your copy is current. A
dirty one means the Recommendation moved and your past reports were measured
against a version that no longer exists.

## Scope

Contrast only. Alt text, focus order, heading structure, motion and the other 75
success criteria are out of scope, and the auditor says so rather than guessing.

## Layout

```
auditor/             the drop-in folder
  identity.md        who the auditor is and what it refuses to do
  rules.md           audit order, citation format, severity scale
  examples.md        worked audits, including one it declines to decide
  reference/         the standard itself, dated and hashed
    fetch-standard.py  re-derives the above from w3.org
    MANIFEST.json      source URL, retrieval date, SHA-256
  checker/
    contrast.py      WCAG relative luminance and ratio math
    audit.py         findings, severity, verdicts
check.py             the gate: runs offline, no API key, prints its own count
fixtures/            one clean page, one violating page
TEST_METHOD.md       written and committed before any gate existed
receipts/            what happened when other people ran it
```

The checker lives inside the drop-in on purpose. `rules.md` forbids estimating a
ratio, so a folder without its checker would have to answer "cannot measure" to
everything. The number comes from code or it does not exist.

## Licence

Code: MIT. The excerpts in `reference/` are reproduced from WCAG 2.1 under the
[W3C Document License](https://www.w3.org/copyright/document-license/),
Copyright (c) W3C (MIT, ERCIM, Keio, Beihang). Where this repo and the published
Recommendation disagree, the Recommendation governs.
