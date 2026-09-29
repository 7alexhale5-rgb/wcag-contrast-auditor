# Examples room: the sabotage / citation demo

One job: the single planted-error file that proves the citation gate actually catches bad citations.

## Inputs

- `examples/findings-broken.md` — findings with intentionally wrong `SC` numbers, `quote:` lines,
  or `input:` kinds.
- The checker to run it against: `check.py` (repo root).

## Process

1. To add a new sabotage case, change one `SC` number, `quote:` line, or `input:` kind in
   `findings-broken.md`.
2. Run `python3 check.py examples/findings-broken.md` and confirm it names the exact line and
   check that caught it, and exits non-zero.
3. Record the result in `receipts/DEVIATIONS.md` (not here — this room holds the fixture, not the proof).

## Outputs

- Updated `examples/findings-broken.md`.

## Human check

Alex confirms the gate fires on every planted error, one at a time. Pass: non-zero exit, correct
line named. Fail: the citation gate has a blind spot — file it as a bug in `auditor/`, not here.
