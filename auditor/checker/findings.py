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
  F  the measured ratio, verdict and severity recompute from the input line
  0  before any of that: every reference file hashes to what MANIFEST.json says

A finding with no input line, an unknown mark, or a provision the manifest does
not list is rejected, not skipped. Only what render() printed can be checked;
AAA passes are suppressed in the text report and live in the JSON report.

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
    """Every line that looks like a finding head becomes a finding, indented or not.
    A malformed input line is kept as an error on the finding, never a crash."""
    out, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        m = HEAD.match(line)
        if m:
            cur = m.groupdict(); cur["verdict"] = MARK_VERDICT.get(cur["mark"], "?")
            cur["lines"] = []; cur["errors"] = []; out.append(cur); continue
        if cur is None: continue
        s = line
        if s.startswith("provision: "):
            cur["provision"] = s[len("provision: "):].replace("reference/", "", 1)
        elif s.startswith("quote: "):
            cur["quote"] = s[len("quote: "):].strip('"')
        elif s.startswith("input: "):
            try:
                cur["input"] = dict(kv.split("=", 1) for kv in s[len("input: "):].split())
            except ValueError:
                cur["errors"].append("G_UNPARSEABLE_INPUT: input line is not key=value pairs")
        elif s.startswith("note: "):
            cur["note"] = s[len("note: "):]
        elif s:
            cur["lines"].append(s)
    for f in out:
        f["message"] = " ".join(f.pop("lines"))
        mm = re.search(r"(\d+(?:\.\d+)?):1 against", f["message"])
        f["measured"] = float(mm.group(1)) if mm else None
    return out

def verify_reference(ref_dir: Path = REF) -> list[str]:
    """Check 0: every file the manifest lists hashes to what the manifest says.
    A verbatim quote from a forged provision file is still a forgery, so this
    runs before any citation is judged."""
    import hashlib
    m = json.loads((ref_dir / "MANIFEST.json").read_text())
    bad = []
    for group in ("criteria", "definitions"):
        for key, v in m.get(group, {}).items():
            f = ref_dir / v["file"]
            if not f.exists() or hashlib.sha256(f.read_text().encode()).hexdigest() != v["sha256"]:
                bad.append(f"0_REFERENCE_TAMPERED: reference/{v['file']} does not match MANIFEST.json")
    return bad

def _level_of(provision_text: str) -> str | None:
    m = re.search(r"\(Level (A{1,3})\)", provision_text)
    return m.group(1) if m else None

def citation_gate(f: dict, ref_dir: Path = REF, manifest: dict | None = None) -> list[str]:
    """Return the list of failure codes for one finding. Empty list = citation holds."""
    if manifest is None:
        manifest = json.loads((ref_dir / "MANIFEST.json").read_text())
    codes = list(f.get("errors", []))
    if f.get("verdict") == "?":
        codes.append(f"H_UNKNOWN_MARK: [{f.get('mark')}] is not a mark the checker prints")
    crit = f.get("criterion")
    entry = manifest.get("criteria", {}).get(crit)
    if entry is None:
        codes.append(f"A_UNKNOWN_SC: SC {crit} is not in reference/MANIFEST.json")
    # The provision must be a file the manifest lists, so the report text can
    # never point the gate outside reference/.
    listed = {v["file"] for g in ("criteria", "definitions") for v in manifest.get(g, {}).values()}
    prov = f.get("provision")
    if not prov or prov not in listed:
        codes.append(f"B_NO_PROVISION: reference/{prov} is not a file the manifest lists")
        return codes
    if entry is not None and entry["file"] != prov:
        codes.append(f"B_FILE_MISMATCH: SC {crit} lives in reference/{entry['file']}, not reference/{prov}")
    pf = ref_dir / prov
    text = pf.read_text()
    body = normalize(text)
    if not f.get("quote") or normalize(f["quote"]) not in body:
        codes.append(f"C_QUOTE_NOT_VERBATIM: quote is not in reference/{prov}")
    inp = f.get("input")
    if inp is None and f.get("verdict") != "?":
        codes.append("I_NO_INPUT: a finding without its input line cannot be recomputed and is an assertion")
    kind = (inp or {}).get("kind")
    if kind and crit in KIND_FOR and KIND_FOR[crit] != kind and f.get("verdict") != "UNDECIDABLE":
        codes.append(f"D_KIND_MISMATCH: SC {crit} applies to {KIND_FOR[crit]}, element is {kind}")
    lvl = _level_of(text)
    if lvl and f.get("level") != lvl:
        codes.append(f"E_LEVEL_MISMATCH: finding says {f.get('level')}, reference/{prov} says Level {lvl}")
    if inp and f.get("verdict") in ("PASS", "FAIL"):
        el = {"id": f["location"], "fg": inp.get("fg"), "bg": inp.get("bg"), "kind": inp.get("kind", "text")}
        if "font_px" in inp: el["font_px"] = float(inp["font_px"])
        if "bold" in inp: el["bold"] = inp["bold"] == "true"
        want_level = "AAA" if f["mark"] == "aaa " else f.get("level")
        recomputed = [x for x in audit.check_element(el) if x.level == want_level]
        if not recomputed or recomputed[0].verdict != f["verdict"] or \
           (f.get("measured") is not None and recomputed[0].measured != f["measured"]):
            got = (recomputed[0].verdict, recomputed[0].measured) if recomputed else None
            codes.append(f"F_RATIO_MISMATCH: finding says {f['verdict']} {f.get('measured')}:1, checker recomputes {got}")
        if f.get("severity") and recomputed and recomputed[0].severity != f["severity"]:
            codes.append(f"F_SEVERITY_MISMATCH: finding says {f['severity']}, checker recomputes {recomputed[0].severity}")
    return codes

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: findings.py <report.txt or .md>", file=sys.stderr); return 2
    text = Path(sys.argv[1]).read_text()
    tampered = verify_reference()
    for c in tampered: print(f"REJECTED reference/  {c}")
    if tampered:
        print("\nreference/ does not match its manifest; no citation can be trusted until it does")
        return 1
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
