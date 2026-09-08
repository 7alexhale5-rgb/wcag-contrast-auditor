# Task 1 follow-up implementation report

## Scope

Changed only `.github/workflows/check.yml` and added `scripts/verify_spec.py`. No Git mutations. `TEST_METHOD.md` and the approved plan are unchanged.

## Red reproduction

The prior workflow executed a command, captured `$?`, and accepted exactly 1. Replacing the command with `python3 -c "raise RuntimeError(\'crash canary\')"` produced a traceback but the entire CI assertion exited 0. Full output: `task-1-followup-red.txt` in this report directory.

## Fix

The workflow now captures the checker with Python's standard-library subprocess API. It requires child exit 1, an exact stdout line `4 citation(s) checked, 3 rejected`, and empty stderr. It prints both streams before failing, preserving actionable CI output. `sys.executable` retains the selected matrix interpreter. The existing six OS/Python combinations and all other steps remain unchanged.

The source-backed spec verifier accepts `--plan` and `--method`, defaults from its own repository root, checks the approved contract markers and ordered six-task structure, and compares method bytes against read-only `git show 0b57525:TEST_METHOD.md`. Named failures return 1. A complete contract returns 0. It uses no runtime dependencies or hardcoded worktree path.

This verifies explicit written contract markers and the frozen method, not the semantic adequacy or completion of the plan. It does not claim that downstream work is done. The Git object must exist locally; absent history fails closed.

## Green verification

Executed the exact inline Python program extracted from the edited workflow:

- Actual planted report: outer exit 0; child exit 1, correct completion, empty stderr.
- RuntimeError canary: outer exit 1; traceback and named rejection.
- Wrong exit 2 despite expected stdout: outer exit 1.
- Missing completion despite exit 1: outer exit 1.
- Unexpected stderr despite expected completion and exit 1: outer exit 1.

Source verifier temporary-file controls all rejected with exit 1: missing decision, missing scope, duplicate task, missing constraints, missing repeat count, missing no-execution mode, missing Ciaran requirement, missing no-sends restriction, changed method, missing plan, and missing method. Real defaults passed with exit 0, also when launched from an unrelated temporary directory.

`python3 -m unittest discover -s tests -v`: five tests passed.

`python3 check.py`: 131/131 checks across eleven gates passed.

`python3 scripts/verify_spec.py`: passed on local Python 3.14.

`/opt/homebrew/opt/python@3.13/bin/python3.13 scripts/verify_spec.py`: passed.

`git diff --check`: passed.

Full commands, stdout, stderr, and exits are retained in `task-1-followup-green.txt` in this report directory. No claim is made for a new Windows/Linux CI run; the lead must push and verify all six jobs on the resulting commit.

## Plain English

A crash can no longer count as a good rejection. The written plan now has a check of its own. The next step is to run all six hosted checks.
