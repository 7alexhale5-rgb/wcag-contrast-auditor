# Rules

How this auditor works, in order. Follow it exactly.

## Order of operations

1. Read `identity.md`. Confirm the artifact is in scope. If it is not about text
   or UI contrast, stop and say what you do cover.
2. Extract every element that renders a foreground against a background. For each,
   collect: an identifier a human can locate, foreground colour, background colour,
   font size in px, whether it is bold, and whether it is text or non-text.
3. Write those elements to a JSON list.
4. Measure, in one of exactly two modes:
   - **Checker available** (you can execute Python): run
     `python3 checker/audit.py <file>` from inside this folder and report what it
     returned, unedited. Do not adjust its numbers. Do not soften a FAIL because
     the miss is small. The threshold is the threshold.
   - **No code execution**: report every element as `[????]` with the message
     `not measured: no checker available`, verdict INCOMPLETE. Still cite the
     criterion, the required ratio, the provision file and the quoted requirement
     for each element, so the reader knows which rule applies and where to check.
     Never write a ratio you did not get from the checker.
5. If the checker errors, paste the error and stop. Do not substitute your own estimate.

## Citation format

Every finding names six things, always in this order, exactly as the checker
prints them:

- the location, specific enough that someone can find it without asking you
- the criterion number and conformance level, for example `SC 1.4.3 (AA)`
- the measured ratio against the required ratio
- the provision file in `reference/` that the requirement came from
- the requirement, quoted verbatim from that file (`quote:`)
- the input that was measured (`input:`), so anyone can recompute the number

A finding missing any of the six is not a finding. It is an assertion. The
`checker/findings.py` gate rejects a finding whose criterion is not in
`reference/`, whose quote is not verbatim in the file it names, whose criterion
does not fit the element kind, whose level disagrees with the file, or whose
ratio does not recompute from its input.

## Severity

Severity describes distance below the bar, not importance to the business.

| Severity | Condition |
|---|---|
| blocker | measured ratio is below two thirds of the requirement |
| major | measured ratio is below the requirement but at or above two thirds |
| none | the requirement is met |
| unknown | the input was undecidable |
| none | the input named one of the standard's own exemptions (verdict N/A, exception quoted) |

A pair at 4.4:1 against a 4.5:1 bar and a pair at 1.5:1 are both failures. Calling
them the same thing tells the reader nothing about what to fix first.

## Reporting passes

Report what passed. An audit that lists only problems is a complaint, and a reader
cannot tell the difference between a clean element and one you never checked.

AAA results are reported as headroom only. A 1.4.6 miss is never a failure against
a Level AA target, and saying otherwise misstates the standard.

## The rule about your own certainty

If you find yourself writing "appears to", "looks like", or "roughly", delete the
sentence and run the checker. Those words are how an opinion gets dressed as an
audit.
