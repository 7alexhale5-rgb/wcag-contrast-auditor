#!/usr/bin/env python3
"""Prove this auditor can fail.

The brief's losing condition is an unverifiable auditor. A gate that has only ever
run green has proved nothing: it may be passing because it is broken. So every check
here is adversarial against our own code.

Four classes:
  1 ANCHOR      the ratio math matches values W3C publishes
  2 MUTATION    break each rule on purpose, demand it goes red
  3 SILENCE     compliant input must produce zero findings (no invented violations)
  4 INVARIANCE  the same violation, expressed three ways, must fire all three times
  5 PURITY      the deterministic layer must not reach the network or a model
"""
from __future__ import annotations
import ast, copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "auditor" / "checker"))
import contrast, audit  # noqa: E402

FAILS: list[str] = []

def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'  <- ' + detail if detail and not cond else ''}")
    if not cond:
        FAILS.append(name)

# --- 1 ANCHOR ---------------------------------------------------------------
# These are the canonical boundary values. #767676 on white is the exact point
# where 1.4.3 AA is met for normal text; #777777 is the first step below it.
print("\n[1] ANCHOR: ratio math against W3C's published values")
for fg, bg, want in [("#000000", "#ffffff", 21.0), ("#ffffff", "#ffffff", 1.0),
                     ("#767676", "#ffffff", 4.5), ("#777777", "#ffffff", 4.4)]:
    got = contrast.round_ratio(contrast.contrast_ratio(fg, bg))
    check(f"{fg} on {bg} == {want}:1", got == want, f"got {got}")
check("ratio is symmetric", contrast.contrast_ratio("#123456", "#fedcba")
                          == contrast.contrast_ratio("#fedcba", "#123456"))
check("rounding never rounds a fail up to the bar",
      contrast.round_ratio(4.4999) == 4.4, f"got {contrast.round_ratio(4.4999)}")

# --- 2 MUTATION -------------------------------------------------------------
# Each rule gets an input built to violate exactly it. If the rule stays quiet,
# the rule is decorative.
print("\n[2] MUTATION: each rule must go red on input built to break it")
MUTANTS = {
    "1.4.3 normal text below 4.5:1":
        {"id": "m", "fg": "#777777", "bg": "#ffffff", "font_px": 16, "kind": "text"},
    "1.4.3 large text below 3:1":
        {"id": "m", "fg": "#bbbbbb", "bg": "#ffffff", "font_px": 32, "kind": "text"},
    "1.4.11 non-text below 3:1":
        {"id": "m", "fg": "#dddddd", "bg": "#ffffff", "kind": "nontext"},
}
for label, el in MUTANTS.items():
    fs = [f for f in audit.check_element(el) if f.level == "AA"]
    check(f"{label} -> FAIL", any(f.verdict == "FAIL" for f in fs),
          f"got {[f.verdict for f in fs]}")

# The large-text exception must be real, not cosmetic: the identical colour pair
# passes at 32px and fails at 16px. If both agree, the exception is not wired in.
pair = {"fg": "#949494", "bg": "#ffffff", "kind": "text"}
small = [f for f in audit.check_element({**pair, "id": "s", "font_px": 16}) if f.level == "AA"][0]
large = [f for f in audit.check_element({**pair, "id": "l", "font_px": 32}) if f.level == "AA"][0]
check("large-text exception actually changes the verdict",
      small.verdict == "FAIL" and large.verdict == "PASS",
      f"16px={small.verdict} 32px={large.verdict}")

# Severity must discriminate. A near miss and an unreadable pair cannot share a label.
near = audit._severity(4.0, 4.5)
gone = audit._severity(1.5, 4.5)
check("severity separates a near miss from unreadable", near != gone, f"{near} vs {gone}")

# --- 3 SILENCE --------------------------------------------------------------
# The failure nobody tests for. An auditor that always finds something is a
# complaint generator; it looks identical to a working one on broken input.
print("\n[3] SILENCE: compliant input must produce no AA failures")
rep = audit.audit(json.loads((ROOT / "fixtures/clean.json").read_text()))
check("compliant fixture returns verdict PASS", rep["verdict"] == "PASS", rep["verdict"])
check("compliant fixture invents zero failures", rep["summary"]["aa_fail"] == 0,
      str(rep["summary"]))
# And it must not go quiet on the broken one.
rep2 = audit.audit(json.loads((ROOT / "fixtures/violating.json").read_text()))
check("violating fixture returns verdict FAIL", rep2["verdict"] == "FAIL", rep2["verdict"])

# --- 4 INVARIANCE -----------------------------------------------------------
# Leo Saraiva's test, adopted: keep one real violation intact and vary how it is
# written. If the finding fires on only some spellings, the auditor is reading
# syntax, not the provision.
print("\n[4] INVARIANCE: one violation, five spellings, five identical verdicts")
SAME_VIOLATION = [
    {"id": "hex6",  "fg": "#777777",            "bg": "#ffffff",        "font_px": 16, "kind": "text"},
    {"id": "hex3",  "fg": "#777",               "bg": "#fff",           "font_px": 16, "kind": "text"},
    {"id": "upper", "fg": "#777777".upper(),    "bg": "#FFFFFF",        "font_px": 16, "kind": "text"},
    {"id": "rgb",   "fg": "rgb(119, 119, 119)", "bg": "rgb(255,255,255)","font_px": 16, "kind": "text"},
    {"id": "rgba1", "fg": "rgba(119,119,119,1)","bg": "white",          "font_px": 16, "kind": "text"},
]
verdicts, ratios = [], []
for el in SAME_VIOLATION:
    f = [x for x in audit.check_element(el) if x.level == "AA"][0]
    verdicts.append(f.verdict); ratios.append(f.measured)
check("all five spellings produce the same verdict", len(set(verdicts)) == 1, str(verdicts))
check("all five spellings produce the same ratio", len(set(ratios)) == 1, str(ratios))
check("and that shared verdict is FAIL", verdicts[0] == "FAIL", verdicts[0])

# --- 5 PURITY ---------------------------------------------------------------
# A "deterministic" check that quietly calls a model is not deterministic. Read
# our own source and refuse to pass if it imports anything that could.
print("\n[5] PURITY: the deterministic layer reaches nothing outside itself")
BANNED = {"requests", "urllib", "httpx", "socket", "http", "openai", "anthropic",
          "random", "aiohttp", "subprocess", "boto3"}
for src in ["auditor/checker/contrast.py", "auditor/checker/audit.py"]:
    tree = ast.parse((ROOT / src).read_text())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    bad = found & BANNED
    check(f"{src} imports nothing that reaches out", not bad, f"found {bad}")

# The reference copy must be present and dated, or a clean report is unfalsifiable.
print("\n[6] PROVENANCE: the cited standard is in the repo, dated, hashed, with its status")
man = ROOT / "auditor/reference/MANIFEST.json"
check("auditor/reference/MANIFEST.json exists", man.exists())
if man.exists():
    m = json.loads(man.read_text())
    check("manifest records the retrieval date", bool(m.get("fetched_utc")))
    check("manifest pins a hash of the source document", len(m.get("source_sha256", "")) == 64)
    check("manifest records the document status", "Recommendation" in m.get("status", ""), m.get("status", ""))
    listed = {**{k: v["file"] for k, v in m.get("criteria", {}).items()},
              **{k: v["file"] for k, v in m.get("definitions", {}).items()}}
    for key, fname in sorted(listed.items()):
        f = ROOT / "auditor/reference" / fname
        check(f"{key}: {fname} exists on disk", f.exists())
        if f.exists():
            body = f.read_text()
            check(f"{key}: file carries the W3C status line", "Status: W3C Recommendation" in body)
            check(f"{key}: file hash matches the manifest",
                  __import__("hashlib").sha256(body.encode()).hexdigest() == m["criteria" if key in m.get("criteria", {}) else "definitions"][key]["sha256"])
    cited = {x.provision_file for el in
             [{"id": "x", "fg": "#777", "bg": "#fff", "font_px": 16, "kind": "text"},
              {"id": "y", "fg": "#777", "bg": "#fff", "kind": "nontext"}]
             for x in audit.check_element(el)}
    for f in sorted(cited):
        check(f"cited provision {f} is listed in the manifest", f in listed.values())

print("\n" + "=" * 62)
if FAILS:
    print(f"SELF-TEST FAILED: {len(FAILS)} check(s) red")
    for f in FAILS: print(f"  - {f}")
    sys.exit(1)
print("SELF-TEST PASSED: every rule was shown to fail on purpose, stay quiet on")
print("compliant input, and hold across five spellings of the same violation.")
