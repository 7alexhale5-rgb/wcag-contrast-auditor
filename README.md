# The Auditor: WCAG 2.1 contrast, cited to the provision

Comp 12 entry (the brief post is titled "#11"; the judges confirmed the numbering slip in-thread).

**Drop `auditor/` into a Claude project, hand it colour pairs, and get back what
passes, what fails, by how much, and which success criterion says so, with the
provision text sitting in the folder where you can check it.**

Built for Clief Notes "The Auditor" with Claude Code. The receipts name who ran
each test.

## Falsify it in thirty seconds

No API key. No network. No install. Python 3, standard library only.

```bash
git clone https://github.com/7alexhale5-rgb/wcag-contrast-auditor.git
cd wcag-contrast-auditor
python3 check.py
```

Last clean-clone run, pasted from `receipts/CLEAN_CLONE.md`:

```
131 checks in 11 gates: 131 passed, 0 failed
GATE PASSED. What each gate proved is in its own lines above; what a gate
looks like when it fails is in receipts/DEVIATIONS.md.
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
| Standard actually in `reference/`? | Yes, six files. `auditor/reference/fetch-standard.py` re-derives them from w3.org; retrieval date and page hash live in the manifest so a re-fetch leaves unchanged text byte-identical. The page hash recorded on 2026-09-07 (commit 3c4c29c) equals the one recorded on 2026-09-08 (current manifest). |
| Can a stranger figure it out? | `auditor/README.md` is the door. `receipts/RUN_C_COLD_MODEL.md` records two fresh model sessions that had never seen it, one able to run code and one not, against an answer key committed first. The stranger run (a named person, on tape, transcript verbatim) lands in `receipts/RUN_B_STRANGER.md` when it happens; until that file exists, no claim about it is made here. |

## Audit your own colours

```bash
python3 auditor/checker/audit.py your-pairs.json
```

Input shape and the six-part finding are in `auditor/README.md`. Exit 0 passes,
1 has a Level AA failure, 2 could not measure something and says what.

## What it reports that an opinion would not

- **Pass and fail.** A clean page produces one `[pass]` line per element, not silence.
- **Headroom, not failure, for AAA.** A miss against 1.4.6 prints as `[aaa ]`. Calling it a failure at a Level AA target would misstate the standard.
- **UNDECIDABLE instead of a guess.** Transparent colour, missing font size, unknown format: the finding says what is missing and the audit is INCOMPLETE with exit code 2. It never estimates.
- **N/A with the exception quoted.** Mark an element `"exempt": "logotype"` and it cites the Logotypes clause. It never decides on its own that text is a logo.
- **The number comes from code.** `auditor/checker/contrast.py` is the WCAG relative-luminance formula and nothing else. The PURITY gate reads its own source and fails if it imports anything that could reach a network or a model.

## Real territory, not only synthetic fixtures

`fixtures/brands/` holds 58 public design-token files from the VoltAgent
awesome-design-md catalog, each naming the upstream file at a pinned commit, its
hash, and whether the local copy matched it at build time. The TERRITORY gate
re-audits all 58 against committed verdicts; the DIFFERENTIAL gate compares 208
colour pairs against an independent luminance implementation; six pairs were
checked by hand against WebAIM before the gate existed. 48 brands fail Level AA
on at least one pair, 8 pass, 2 are incomplete because a token carries
transparency. Airbnb's white-on-Rausch button text is 3.5:1. Anthropic's
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
| `auditor/` | The drop-in folder: `README.md`, `identity.md`, `rules.md`, `examples.md`, `reference/`, and `checker/`. The checker lives inside because `rules.md` forbids estimating; without it every ratio is UNDECIDABLE, which is what the folder says in a project that cannot run code (example 5). |
| `check.py` | The gate. 11 named gates, prints its own count. |
| `fixtures/` | Two synthetic pages, one exemption case, 58 brand token files, and the builder that made them. |
| `examples/findings-broken.md` | Wrong on purpose, so a bare run fires. |
| `receipts/` | `DEVIATIONS.md` (defects found and gates shown red, dated), `CLEAN_CLONE.md`, `EXPECTED-brands.json`, `EXPECTED-cold-model.md` (committed before the run), stranger and cold-model transcripts, and the README as it was before each rewrite. |
| `TEST_METHOD.md` | Written and committed before any gate existed (commit `0b57525`). Not edited since. |

## Licence

Code: MIT (`LICENSE`). The excerpts in `auditor/reference/` are reproduced from
WCAG 2.1 under the W3C Document License, Copyright (c) W3C (MIT, ERCIM, Keio,
Beihang), and are not covered by the MIT licence. Where this repo and the
published Recommendation disagree, the Recommendation governs.
