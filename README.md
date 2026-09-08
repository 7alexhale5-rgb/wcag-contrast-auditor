# The Auditor: WCAG 2.1 contrast, cited to the provision

**Drop `auditor/` into a Claude project, hand it colour pairs, and get back what
passes, what fails, by how much, and which success criterion says so, with the
provision text sitting in the folder where you can check it.**

Built for Clief Notes Comp 12 "The Auditor" with Claude Code. The receipts name
who ran each test.

## Falsify it in thirty seconds

No API key. No network. No install. Python 3, standard library only.

```bash
git clone https://github.com/7alexhale5-rgb/wcag-contrast-auditor.git
cd wcag-contrast-auditor
python3 check.py
```

Last clean-clone run, pasted from `receipts/CLEAN_CLONE.md`:

```
114 checks in 11 gates: 114 passed, 0 failed
GATE PASSED: every rule was shown to fail on purpose, stay quiet on compliant
input, hold across five spellings, cite only what is on disk, and recompute.
```

The run includes the citation gate firing on three planted bad citations in
`examples/findings-broken.md`. Now plant your own: change any `SC` number,
`quote:` line, or `input:` kind in that file and run

```bash
python3 check.py examples/findings-broken.md
```

It names the line and the check that caught it, and exits non-zero. Every gate
has also been shown red on purpose, one sabotage at a time, in
`receipts/DEVIATIONS.md`. The same command runs on every push on three operating
systems and two Python versions; the check-run is on the Actions tab and its
first result is pasted in `receipts/CLEAN_CLONE.md`.

## The four things this is judged on, and where to check each

| Question | Where to look |
|---|---|
| Audits a real, citable standard? | `auditor/reference/`: WCAG 2.1 SC 1.4.3, 1.4.11, 1.4.6 and the three glossary definitions the math comes from, verbatim, with the W3C licence, the document status (W3C Recommendation 06 May 2025), and a hash per file in `MANIFEST.json`. `python3 check.py --verify-reference` lists them. |
| Findings specific and located, with severity? | Every finding has six parts: location, `SC n.n.n (level)`, measured ratio against required, provision file, the requirement quoted from it, and the input measured. Severity is blocker or major by distance below the bar. `auditor/examples.md` holds four real runs; the EXAMPLES gate refuses to pass if any block differs from a live run. |
| Standard actually in `reference/`? | Yes, six files. `auditor/reference/fetch-standard.py` re-derives them from w3.org; retrieval date and page hash live in the manifest so a re-fetch leaves unchanged text byte-identical. The live page hashed identically on 2026-09-07 and 2026-09-08. |
| Can a stranger figure it out? | `auditor/README.md` is the door. The receipts folder records what happened when people and models who had never seen it tried: `RUN_B_STRANGER.md`, `RUN_C_COLD_MODEL.md`. The README is rewritten from where they stalled, and the earlier version is kept. |

## What it reports that an opinion would not

- **Pass and fail.** A clean page produces one `[pass]` line per element, not silence.
- **Headroom, not failure, for AAA.** A miss against 1.4.6 prints as `[aaa ]`. Calling it a failure at a Level AA target would misstate the standard.
- **UNDECIDABLE instead of a guess.** Transparent colour, missing font size, unknown format: the finding says what is missing and the audit is INCOMPLETE with exit code 2. It never estimates.
- **N/A with the exception quoted.** Mark an element `"exempt": "logotype"` and it cites the Logotypes clause. It never decides on its own that text is a logo.
- **The number comes from code.** `auditor/checker/contrast.py` is the WCAG relative-luminance formula and nothing else. The PURITY gate reads its own source and fails if it imports anything that could reach a network or a model.

## Real territory, not only synthetic fixtures

`fixtures/brands/` holds 59 public design-token files from the VoltAgent
awesome-design-md catalog, each with its source URL and a hash of the local copy.
The TERRITORY gate re-audits all 59 against committed verdicts; the DIFFERENTIAL
gate compares 209 colour pairs against an independent luminance implementation;
six pairs were checked by hand against WebAIM before the gate existed. 48 brands
fail Level AA on at least one pair, 8 pass, 3 are incomplete because a token
carries transparency. Airbnb's white-on-Rausch button text is 3.5:1. Anthropic's
white on terracotta is 3.2:1.

The pairing rule (which token is text on which) is published in
`fixtures/build_brand_fixtures.py` so you can disagree with it. Divider tokens
carry a note that 1.4.11 covers control outlines, not decorative lines.

## What the gate cannot catch

It proves a cited provision exists, its quote is verbatim, its level and kind
fit, and its ratio recomputes. It cannot prove the citation is the right one for
the element in front of it. That judgment stays human, and the checker says so
in its own output.

## What's in the repo

| Path | |
|---|---|
| `auditor/` | The drop-in folder: `README.md`, `identity.md`, `rules.md`, `examples.md`, `reference/`, and `checker/`. The checker lives inside because `rules.md` forbids estimating; a folder that cannot measure would have to answer "cannot measure" to everything. |
| `check.py` | The gate. 11 named gates, prints its own count. |
| `fixtures/` | Two synthetic pages, one exemption case, 59 brand token files, and the builder that made them. |
| `examples/findings-broken.md` | Wrong on purpose, so a bare run fires. |
| `receipts/` | `DEVIATIONS.md` (defects found and gates shown red, dated), `CLEAN_CLONE.md`, `EXPECTED-brands.json`, `EXPECTED-cold-model.md` (committed before the run), stranger and cold-model transcripts, and the README as it was before each rewrite. |
| `TEST_METHOD.md` | Written and committed before any gate existed (commit `0b57525`). Not edited since. |

## Licence

Code: MIT (`LICENSE`). The excerpts in `auditor/reference/` are reproduced from
WCAG 2.1 under the W3C Document License, Copyright (c) W3C (MIT, ERCIM, Keio,
Beihang), and are not covered by the MIT licence. Where this repo and the
published Recommendation disagree, the Recommendation governs.
