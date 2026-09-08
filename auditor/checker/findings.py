#!/usr/bin/env python3
"""Parse a findings report and check every citation against reference/.

This is the gate a judge plants a fake citation to test. It reads the report
text (the exact shape audit.py prints), and for each finding checks:

  A  the criterion number exists in reference/MANIFEST.json
  B  the provision file it names exists on disk
  C  the quoted requirement is a verbatim substring of that file (whitespace
     normalised, because the published text is hard-wrapped)
  D  the criterion fits the element kind (1.4.11 is never cited for text;
     1.4.3 and 1.4.6 never for nontext)
  E  the level in the finding matches the "(Level X)" line in the provision file
  F  the measured ratio and verdict recompute from the input line

What it cannot check, said plainly: that the citation is the RIGHT one for the
element. A finding can cite a real provision, quote it verbatim, and still be
about the wrong thing. That judgment stays human.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit  # noqa: E402

REF = HERE.parent / "reference"
KIND_FOR = {"1.4.3": "text", "1.4.6": "text", "1.4.11": "nontext"}

HEAD = re.compile(r"^\[(?P<mark>[^\]]{4})\] (?P<location>.+?)  SC (?P<criterion>[\d.]+) \((?P<level>\w+)\)(?:  severity=(?P<severity>\w+))?$")
MARK_VERDICT = {"pass": "PASS", "FAIL": "FAIL", "????": "UNDECIDABLE", "n/a ": "N/A", "aaa ": "FAIL"}

def normalize(s: str) -> str:
    return " ".join(s.split())

def parse_findings(text: str) -> list[dict]:
    out, cur = [], None
    for line in text.splitlines():
        m = HEAD.match(line)
        if m:
            cur = m.groupdict(); cur["verdict"] = MARK_VERDICT.get(cur["mark"], "?")
            cur["lines"] = []; out.append(cur); continue
        if cur is None: continue
        s = line.strip()
        if s.startswith("provision: "):
            cur["provision"] = s[len("provision: "):].replace("reference/", "", 1)
        elif s.startswith("quote: "):
            cur["quote"] = s[len("quote: "):].strip('"')
        elif s.startswith("input: "):
            cur["input"] = dict(kv.split("=", 1) for kv in s[len("input: "):].split())
        elif s.startswith("note: "):
            cur["note"] = s[len("note: "):]
        elif s:
            cur["lines"].append(s)
    for f in out:
        f["message"] = " ".join(f.pop("lines"))
        mm = re.search(r"(\d+(?:\.\d+)?):1 against", f["message"])
        f["measured"] = float(mm.group(1)) if mm else None
    return out

def _level_of(provision_text: str) -> str | None:
    m = re.search(r"\(Level (A{1,3})\)", provision_text)
    return m.group(1) if m else None

def citation_gate(f: dict, ref_dir: Path = REF, manifest: dict | None = None) -> list[str]:
    """Return the list of failure codes for one finding. Empty list = citation holds."""
    if manifest is None:
        manifest = json.loads((ref_dir / "MANIFEST.json").read_text())
    codes = []
    crit = f.get("criterion")
    if crit not in manifest.get("criteria", {}):
        codes.append(f"A_UNKNOWN_SC: SC {crit} is not in reference/MANIFEST.json")
    pf = ref_dir / f.get("provision", "")
    if not f.get("provision") or not pf.exists():
        codes.append(f"B_NO_PROVISION: reference/{f.get('provision')} is not on disk")
        return codes
    body = normalize(pf.read_text())
    if not f.get("quote") or normalize(f["quote"]) not in body:
        codes.append(f"C_QUOTE_NOT_VERBATIM: quote is not in reference/{f['provision']}")
    kind = (f.get("input") or {}).get("kind")
    if kind and crit in KIND_FOR and KIND_FOR[crit] != kind:
        codes.append(f"D_KIND_MISMATCH: SC {crit} applies to {KIND_FOR[crit]}, element is {kind}")
    lvl = _level_of(pf.read_text())
    if lvl and f.get("level") != lvl:
        codes.append(f"E_LEVEL_MISMATCH: finding says {f.get('level')}, reference/{f['provision']} says Level {lvl}")
    inp = f.get("input")
    if inp and f.get("verdict") in ("PASS", "FAIL") and f["mark"] != "aaa ":
        el = {"id": f["location"], "fg": inp.get("fg"), "bg": inp.get("bg"), "kind": inp.get("kind", "text")}
        if "font_px" in inp: el["font_px"] = float(inp["font_px"])
        if "bold" in inp: el["bold"] = inp["bold"] == "true"
        recomputed = [x for x in audit.check_element(el) if x.level == f.get("level")]
        if not recomputed or recomputed[0].verdict != f["verdict"] or \
           (f.get("measured") is not None and recomputed[0].measured != f["measured"]):
            got = (recomputed[0].verdict, recomputed[0].measured) if recomputed else None
            codes.append(f"F_RATIO_MISMATCH: finding says {f['verdict']} {f.get('measured')}:1, checker recomputes {got}")
    return codes

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: findings.py <report.txt or .md>", file=sys.stderr); return 2
    text = Path(sys.argv[1]).read_text()
    findings = parse_findings(text)
    bad = 0
    for f in findings:
        codes = citation_gate(f)
        status = "holds" if not codes else "REJECTED"
        print(f"{status:8} {f['location']}  SC {f['criterion']} ({f['level']})")
        for c in codes: print(f"           {c}"); 
        bad += bool(codes)
    print(f"\n{len(findings)} citation(s) checked, {bad} rejected")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
