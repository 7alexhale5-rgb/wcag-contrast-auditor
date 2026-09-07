#!/usr/bin/env python3
"""Turn measured contrast into cited findings against WCAG 2.1.

Reports PASS and FAIL, because an audit that only lists problems is a complaint.
Reports UNDECIDABLE where the input does not carry enough information, because a
guessed ratio is worse than an admitted gap.
"""
from __future__ import annotations
import json, sys, argparse
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contrast import (contrast_ratio, round_ratio, is_large_text, parse_color,
                      ColorError, AA_NORMAL, AA_LARGE, AA_NONTEXT,
                      AAA_NORMAL, AAA_LARGE, Threshold)

REF = Path(__file__).resolve().parent.parent / "reference"

@dataclass
class Finding:
    verdict: str        # PASS | FAIL | UNDECIDABLE
    criterion: str      # "1.4.3"
    level: str          # "AA"
    severity: str       # blocker | major | none | unknown
    location: str
    measured: float | None
    required: float
    message: str
    provision_file: str

def _severity(ratio: float, required: float) -> str:
    # Distance below the bar decides severity. Under 3:1 on a 4.5:1 rule is not
    # a near miss, it is unreadable for the users the criterion exists to protect.
    if ratio >= required: return "none"
    return "blocker" if ratio < required * 0.67 else "major"

def check_element(el: dict) -> list[Finding]:
    """el: {id, fg, bg, font_px?, bold?, kind: 'text'|'nontext'}"""
    loc = el.get("id", "<unnamed>")
    kind = el.get("kind", "text")
    try:
        fg, bg = parse_color(el["fg"]), parse_color(el["bg"])
    except (ColorError, KeyError) as e:
        return [Finding("UNDECIDABLE", "1.4.3", "AA", "unknown", loc, None,
                        AA_NORMAL.ratio, f"cannot measure: {e}", "wcag21-1.4.3.md")]
    ratio = round_ratio(contrast_ratio(fg, bg))
    out: list[Finding] = []

    if kind == "nontext":
        t = AA_NONTEXT
        out.append(Finding(
            "PASS" if ratio >= t.ratio else "FAIL", t.criterion, t.level,
            _severity(ratio, t.ratio), loc, ratio, t.ratio,
            f"{ratio}:1 against a {t.ratio}:1 minimum for {t.applies_to}",
            "wcag21-1.4.11.md"))
        return out

    font_px, bold = el.get("font_px"), bool(el.get("bold", False))
    if font_px is None:
        out.append(Finding("UNDECIDABLE", "1.4.3", "AA", "unknown", loc, ratio,
                           AA_NORMAL.ratio,
                           f"measured {ratio}:1 but no font size given, so the "
                           f"large-text exception cannot be resolved",
                           "wcag21-1.4.3.md"))
        return out

    large = is_large_text(float(font_px), bold)
    aa = AA_LARGE if large else AA_NORMAL
    aaa = AAA_LARGE if large else AAA_NORMAL
    out.append(Finding(
        "PASS" if ratio >= aa.ratio else "FAIL", aa.criterion, aa.level,
        _severity(ratio, aa.ratio), loc, ratio, aa.ratio,
        f"{ratio}:1 against a {aa.ratio}:1 minimum for {aa.applies_to} "
        f"(measured at {font_px}px{', bold' if bold else ''})",
        "wcag21-1.4.3.md"))
    # AAA is reported as headroom only. Never a failure at AA conformance.
    out.append(Finding(
        "PASS" if ratio >= aaa.ratio else "FAIL", aaa.criterion, "AAA",
        "none", loc, ratio, aaa.ratio,
        f"AAA headroom: {ratio}:1 against {aaa.ratio}:1. Not required for AA.",
        "wcag21-1.4.6.md"))
    return out

def audit(elements: list[dict]) -> dict:
    findings = [f for el in elements for f in check_element(el)]
    aa = [f for f in findings if f.level == "AA"]
    return {
        "standard": "WCAG 2.1 (W3C Recommendation)",
        "conformance_target": "Level AA",
        "provisions_dir": str(REF),
        "summary": {
            "elements": len(elements),
            "aa_pass": sum(f.verdict == "PASS" for f in aa),
            "aa_fail": sum(f.verdict == "FAIL" for f in aa),
            "undecidable": sum(f.verdict == "UNDECIDABLE" for f in aa),
            "blockers": sum(f.severity == "blocker" for f in aa),
        },
        "verdict": ("FAIL" if any(f.verdict == "FAIL" for f in aa)
                    else "INCOMPLETE" if any(f.verdict == "UNDECIDABLE" for f in aa)
                    else "PASS"),
        "findings": [asdict(f) for f in findings],
    }

def render(rep: dict) -> str:
    s = rep["summary"]
    L = [f"WCAG 2.1 Level AA contrast audit",
         f"verdict: {rep['verdict']}",
         f"{s['elements']} element(s): {s['aa_pass']} pass, {s['aa_fail']} fail, "
         f"{s['undecidable']} undecidable, {s['blockers']} blocker(s)", ""]
    for f in rep["findings"]:
        if f["level"] == "AAA" and f["verdict"] == "PASS":
            continue  # headroom noise; the JSON still carries it
        mark = {"PASS": "pass", "FAIL": "FAIL", "UNDECIDABLE": "????"}[f["verdict"]]
        L.append(f"[{mark}] {f['location']}  SC {f['criterion']} ({f['level']})"
                 f"{'  severity=' + f['severity'] if f['severity'] not in ('none','unknown') else ''}")
        L.append(f"        {f['message']}")
        L.append(f"        provision: reference/{f['provision_file']}")
    return "\n".join(L)

def main() -> int:
    p = argparse.ArgumentParser(description="Audit colour pairs against WCAG 2.1 AA contrast.")
    p.add_argument("input", help="JSON file: a list of {id, fg, bg, font_px, bold, kind}")
    p.add_argument("--json", action="store_true", help="emit the full report as JSON")
    a = p.parse_args()
    rep = audit(json.loads(Path(a.input).read_text()))
    print(json.dumps(rep, indent=2) if a.json else render(rep))
    return 1 if rep["verdict"] == "FAIL" else 0

if __name__ == "__main__":
    sys.exit(main())
