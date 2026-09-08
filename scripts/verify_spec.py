#!/usr/bin/env python3
"""Check the approved execution contract and frozen test method, offline."""

import argparse
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def verify(plan_path, method_path):
    failures = []
    try:
        plan = plan_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"PLAN_READ: {exc}")
        plan = ""

    sections = {
        title: body
        for title, body in re.findall(
            r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", plan, re.M | re.S
        )
    }
    decision = sections.get("Decision and verifier", "")
    if not all(
        term in decision
        for term in (
            "SC 1.4.3",
            "1.4.11 at AA",
            "1.4.6 as AAA headroom",
            "Verifier:",
            "local and CI gate",
            "all 60 frozen AI conformance trials",
        )
    ):
        failures.append(
            "DECISION_VERIFIER: missing scope or executable acceptance contract"
        )

    tasks = re.findall(r"^## Task (\d+): (.+)$", plan, re.M)
    if [number for number, _ in tasks] != [str(n) for n in range(1, 7)] or len(
        {title for _, title in tasks}
    ) != 6:
        failures.append("TASK_ORDER: expected six unique tasks numbered 1 through 6")

    constraints = sections.get("Global Constraints", "")
    for term in (
        "Python standard library only, offline",
        "Preserve TEST_METHOD.md exactly",
        "six existing entries",
        "Audit exit 0",
        "1 means an AA failure",
        "2 means INCOMPLETE",
        "One implementer writes at a time",
        "Subagents never mutate Git state",
        "failing regression before a fix",
        "No private corpus",
        "Do not rewrite global tools",
    ):
        if term not in constraints:
            failures.append(f"GLOBAL_CONSTRAINT: missing {term!r}")

    if not all(
        term in plan
        for term in (
            "Ciaran is the only human tester",
            "Ciaran's recorded no-help test exists",
            "Completion remains open until that outcome is recorded",
            "Alex alone sends the invitation and competition comment",
            "Alex sends all messages",
        )
    ):
        failures.append(
            "HUMAN_SEND_BOUNDARY: missing Ciaran-only or Alex-only requirement"
        )

    evaluation = sections.get(
        "Task 5: Development coverage and reproducible AI evaluation harness", ""
    )
    if not all(
        term in evaluation
        for term in (
            "Freeze six JSON cases",
            "Five fresh runs of each per mode =60",
            "measured mode",
            "no-execution mode",
            "smoke trials are marked pilot and cannot count",
        )
    ):
        failures.append(
            "EVALUATION_CONTRACT: expected six cases, five repeats, two modes, 60 trials"
        )

    try:
        frozen = subprocess.run(
            ["git", "-C", str(ROOT), "show", "0b57525:TEST_METHOD.md"],
            capture_output=True,
            check=True,
        ).stdout
        if method_path.read_bytes() != frozen:
            failures.append("FROZEN_METHOD: TEST_METHOD.md differs from commit 0b57525")
    except (OSError, subprocess.CalledProcessError) as exc:
        failures.append(f"FROZEN_METHOD_READ: {exc}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", type=Path, default=ROOT / ".planning/comp-12-finish/PLAN.md"
    )
    parser.add_argument("--method", type=Path, default=ROOT / "TEST_METHOD.md")
    args = parser.parse_args()
    failures = verify(args.plan.resolve(), args.method.resolve())
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        return 1
    print(
        "PASS SPEC_CONTRACT: six ordered tasks, acceptance boundaries, 60 trials, frozen method"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
