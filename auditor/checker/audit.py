#!/usr/bin/env python3
"""Turn measured contrast into cited findings against WCAG 2.1.

Reports PASS and FAIL, because an audit that only lists problems is a complaint.
Reports UNDECIDABLE where the input does not carry enough information, because a
guessed ratio is worse than an admitted gap. Reports N/A, quoting the exception,
when the input names one of the standard's own exemptions.

Every finding carries the provision file, the requirement quoted verbatim from it,
and the normalised input, so check.py can recompute the ratio and confirm the
quote without trusting this file.
"""
from __future__ import annotations
import json, sys, argparse
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contrast import (contrast_ratio, round_ratio, is_large_text, is_bold, parse_color,
                      ColorError, AA_NORMAL, AA_LARGE, AA_NONTEXT,
                      AAA_NORMAL, AAA_LARGE, EXEMPTIONS, PT_TO_PX, Threshold)

REF = Path(__file__).resolve().parent.parent / "reference"

@dataclass
class Finding:
    verdict: str        # PASS | FAIL | UNDECIDABLE | N/A
    criterion: str      # "1.4.3"
    level: str          # "AA"
    severity: str       # blocker | major | none | unknown
    location: str
    measured: float | None
    required: float
    message: str
    provision_file: str
    quote: str          # verbatim requirement or exception text from that file
    input: dict         # the normalised element, so a reader can recompute the ratio

def _severity(ratio: float, required: float) -> str:
    # Distance below the bar decides severity, and the bar is two thirds of the
    # requirement, as rules.md says. Under that on a 4.5:1 rule is not a near
    # miss, it is unreadable for the users the criterion exists to protect.
    if ratio >= required: return "none"
    return "blocker" if ratio < required * 2 / 3 else "major"

def normalise(el: dict) -> dict:
    """Turn stylesheet-shaped input into what the thresholds need, in code.

    font_pt is converted here (never read as px). font_weight decides bold when
    bold is not given. opacity below 1 is recorded so the colour is refused as
    non-opaque. The model that extracted the element never does this arithmetic.
    """
    out = {"id": el.get("id", "<unnamed>"), "fg": el.get("fg"), "bg": el.get("bg"),
           "kind": el.get("kind", "text")}
    if el.get("exempt") is not None: out["exempt"] = el["exempt"]
    if el.get("font_px") is not None: out["font_px"] = float(el["font_px"])
    elif el.get("font_pt") is not None: out["font_px"] = round(float(el["font_pt"]) * PT_TO_PX, 4)
    if el.get("bold") is not None: out["bold"] = bool(el["bold"])
    elif el.get("font_weight") is not None: out["bold"] = is_bold(el["font_weight"])
    else: out["bold"] = False
    if el.get("opacity") is not None: out["opacity"] = float(el["opacity"])
    if el.get("note"): out["note"] = str(el["note"])
    return out

def _input_str(el: dict) -> str:
    keys = ["fg", "bg", "font_px", "bold", "opacity", "exempt", "kind"]
    return " ".join(f"{k}={str(el[k]).lower() if isinstance(el[k], bool) else el[k]}" for k in keys if k in el)

def check_element(raw: dict) -> list[Finding]:
    """raw: {id, fg, bg, font_px|font_pt?, bold|font_weight?, opacity?, exempt?, kind: 'text'|'nontext'}"""
    el = normalise(raw)
    loc, kind = el["id"], el["kind"]
    if kind not in ("text", "nontext"):
        return [Finding("UNDECIDABLE", "1.4.3", "AA", "unknown", loc, None, AA_NORMAL.ratio,
                        f"cannot audit: kind must be text or nontext, got {kind!r}",
                        "wcag21-1.4.3.md", AA_NORMAL.quote, el)]
    base = AA_NONTEXT if kind == "nontext" else AA_NORMAL   # the criterion this kind is judged under

    if "exempt" in el:
        ex = EXEMPTIONS[kind].get(str(el["exempt"]).lower())
        if ex is None:
            return [Finding("UNDECIDABLE", base.criterion, base.level, "unknown", loc, None, base.ratio,
                            f"exemption {el['exempt']!r} does not exist in SC {base.criterion}; "
                            f"valid for {kind}: {', '.join(sorted(EXEMPTIONS[kind]))}",
                            base.provision_file, base.quote, el)]
        return [Finding("N/A", base.criterion, base.level, "none", loc, None, base.ratio,
                        f"exempt as {el['exempt']}: no contrast requirement applies", ex[1], ex[0], el)]

    if el.get("opacity", 1.0) < 0.999:
        return [Finding("UNDECIDABLE", base.criterion, base.level, "unknown", loc, None, base.ratio,
                        f"cannot measure: opacity {el['opacity']} composites against an unknown backdrop; "
                        f"give the composited colour", base.provision_file, base.quote, el)]
    try:
        fg, bg = parse_color(el["fg"]), parse_color(el["bg"])
    except (ColorError, KeyError, TypeError) as e:
        return [Finding("UNDECIDABLE", base.criterion, base.level, "unknown", loc, None,
                        base.ratio, f"cannot measure: {e}", base.provision_file, base.quote, el)]
    ratio = round_ratio(contrast_ratio(fg, bg))
    out: list[Finding] = []

    if kind == "nontext":
        t = AA_NONTEXT
        out.append(Finding(
            "PASS" if ratio >= t.ratio else "FAIL", t.criterion, t.level,
            _severity(ratio, t.ratio), loc, ratio, t.ratio,
            f"{ratio}:1 against a {t.ratio}:1 minimum for {t.applies_to}",
            t.provision_file, t.quote, el))
        return out

    font_px, bold = el.get("font_px"), el["bold"]
    if font_px is None:
        out.append(Finding("UNDECIDABLE", "1.4.3", "AA", "unknown", loc, ratio,
                           AA_NORMAL.ratio,
                           f"measured {ratio}:1 but no font size given, so the "
                           f"large-text exception cannot be resolved",
                           "wcag21-1.4.3.md", AA_NORMAL.quote, el))
        return out

    large = is_large_text(float(font_px), bold)
    aa = AA_LARGE if large else AA_NORMAL
    aaa = AAA_LARGE if large else AAA_NORMAL
    out.append(Finding(
        "PASS" if ratio >= aa.ratio else "FAIL", aa.criterion, aa.level,
        _severity(ratio, aa.ratio), loc, ratio, aa.ratio,
        f"{ratio}:1 against a {aa.ratio}:1 minimum for {aa.applies_to} "
        f"(measured at {font_px:g}px{', bold' if bold else ''})",
        aa.provision_file, aa.quote, el))
    # AAA is reported as headroom only. Never a failure at AA conformance.
    out.append(Finding(
        "PASS" if ratio >= aaa.ratio else "FAIL", aaa.criterion, "AAA",
        "none", loc, ratio, aaa.ratio,
        f"AAA headroom: {ratio}:1 against {aaa.ratio}:1. Not required for AA.",
        aaa.provision_file, aaa.quote, el))
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
            "not_applicable": sum(f.verdict == "N/A" for f in aa),
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
         f"{s['undecidable']} undecidable, {s['not_applicable']} n/a, {s['blockers']} blocker(s)", ""]
    for f in rep["findings"]:
        if f["level"] == "AAA" and f["verdict"] == "PASS":
            continue  # headroom noise; the JSON still carries it
        if f["level"] == "AAA":
            mark = "aaa "   # an AAA miss is headroom, never a failure at AA
        else:
            mark = {"PASS": "pass", "FAIL": "FAIL", "UNDECIDABLE": "????", "N/A": "n/a "}[f["verdict"]]
        L.append(f"[{mark}] {f['location']}  SC {f['criterion']} ({f['level']})"
                 f"{'  severity=' + f['severity'] if f['severity'] not in ('none','unknown') else ''}")
        L.append(f"        {f['message']}")
        L.append(f"        provision: reference/{f['provision_file']}")
        L.append(f"        quote: \"{f['quote']}\"")
        L.append(f"        input: {_input_str(f['input'])}")
        if f["input"].get("note"):
            L.append(f"        note: {f['input']['note']}")
    return "\n".join(L)

EXIT = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}

def main() -> int:
    p = argparse.ArgumentParser(description="Audit colour pairs against WCAG 2.1 AA contrast.")
    p.add_argument("input", help="JSON file: a list of {id, fg, bg, font_px|font_pt, bold|font_weight, opacity, exempt, kind}, or an object with an elements list")
    p.add_argument("--json", action="store_true", help="emit the full report as JSON")
    a = p.parse_args()
    data = json.loads(Path(a.input).read_text())
    # Accept a bare list of elements, or an object carrying "elements" plus provenance.
    rep = audit(data["elements"] if isinstance(data, dict) else data)
    print(json.dumps(rep, indent=2) if a.json else render(rep))
    return EXIT[rep["verdict"]]  # PASS 0, FAIL 1, INCOMPLETE 2: an undecided audit never passes CI silently

if __name__ == "__main__":
    sys.exit(main())
