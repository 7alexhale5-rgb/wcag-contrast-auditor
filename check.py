#!/usr/bin/env python3
"""The gate. Runs bare, offline, no API key, standard library only.

    python3 check.py                     every gate, prints its own count
    python3 check.py --verify-reference  list every provision and definition on disk
    python3 check.py <findings-file>     run only the citation gate on that file

A gate that has only ever run green has proved nothing: it may be passing because
it is broken. So every check here is adversarial against our own code, and the
gates that can be shown red on purpose are shown red in receipts/DEVIATIONS.md.

What this cannot catch, stated plainly so nobody over-trusts it: the citation
gate proves a cited provision exists and its quote is verbatim. It cannot prove
the citation is the RIGHT one for the element in front of it. That stays human.
"""
from __future__ import annotations
import ast, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDITOR = ROOT / "auditor"
REF = AUDITOR / "reference"
sys.path.insert(0, str(AUDITOR / "checker"))
import contrast, audit, findings  # noqa: E402

FAILS: list[str] = []
COUNT = 0
GATES = 0

def gate(title: str) -> None:
    global GATES
    GATES += 1
    print(f"\n[{GATES}] {title}")

def check(name: str, cond: bool, detail: str = "") -> None:
    global COUNT
    COUNT += 1
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'  <- ' + detail if detail and not cond else ''}")
    if not cond:
        FAILS.append(name)

def aa(el: dict):
    return [f for f in audit.check_element(el) if f.level == "AA"]

# ---------------------------------------------------------------- SHAPE
def gate_shape():
    gate("SHAPE: the drop-in folder holds the declared set and nothing else")
    declared = {"README.md", "identity.md", "rules.md", "examples.md", "reference", "checker"}
    actual = {p.name for p in AUDITOR.iterdir() if not p.name.startswith(".") and p.name != "__pycache__"}
    check("auditor/ exists", AUDITOR.is_dir())
    check("auditor/ has every declared item", not (declared - actual), f"missing {sorted(declared - actual)}")
    check("auditor/ has nothing undeclared", not (actual - declared), f"extra {sorted(actual - declared)}")
    for name in sorted(declared):
        check(f"exact filename: {name}", (AUDITOR / name).exists())

# ----------------------------------------------------------- PROVENANCE
def gate_provenance():
    gate("PROVENANCE: the cited standard is on disk, dated, hashed, with its status")
    man = REF / "MANIFEST.json"
    check("auditor/reference/MANIFEST.json exists", man.exists())
    if not man.exists(): return
    m = json.loads(man.read_text())
    check("manifest records the retrieval date", bool(m.get("fetched_utc")))
    check("manifest pins a hash of the source document", len(m.get("source_sha256", "")) == 64)
    check("manifest records the document status", "Recommendation" in m.get("status", ""), m.get("status", ""))
    listed = {}
    for group in ("criteria", "definitions"):
        for key, v in m.get(group, {}).items():
            listed[v["file"]] = (group, key, v["sha256"])
    for fname, (group, key, sha) in sorted(listed.items()):
        f = REF / fname
        check(f"{key}: {fname} exists on disk", f.exists())
        if f.exists():
            body = f.read_text()
            check(f"{key}: carries the W3C status line", "Status: W3C Recommendation" in body)
            check(f"{key}: carries the W3C licence notice", "W3C Document License" in body)
            check(f"{key}: file hash matches the manifest", hashlib.sha256(body.encode()).hexdigest() == sha)
    used = {t.provision_file for t in (contrast.AA_NORMAL, contrast.AA_LARGE, contrast.AA_NONTEXT,
                                       contrast.AAA_NORMAL, contrast.AAA_LARGE)}
    used |= {v[1] for kind in contrast.EXEMPTIONS.values() for v in kind.values()}
    for f in sorted(used):
        check(f"code cites {f}, which the manifest lists", f in listed)
    # Every quote the code can emit is verbatim in the file it names.
    quotes = [(t.quote, t.provision_file) for t in (contrast.AA_NORMAL, contrast.AA_LARGE, contrast.AA_NONTEXT,
                                                    contrast.AAA_NORMAL, contrast.AAA_LARGE)]
    quotes += [v for kind in contrast.EXEMPTIONS.values() for v in kind.values()]
    for q, f in sorted(set(quotes)):
        body = findings.normalize((REF / f).read_text()) if (REF / f).exists() else ""
        check(f"quote is verbatim in {f}: \"{q[:48]}...\"", findings.normalize(q) in body)

# --------------------------------------------------------------- ANCHOR
def gate_anchor():
    gate("ANCHOR: ratio math against known boundary values")
    for fg, bg, want in [("#000000", "#ffffff", 21.0), ("#ffffff", "#ffffff", 1.0),
                         ("#767676", "#ffffff", 4.5), ("#777777", "#ffffff", 4.4)]:
        got = contrast.round_ratio(contrast.contrast_ratio(fg, bg))
        check(f"{fg} on {bg} == {want}:1", got == want, f"got {got}")
    check("ratio is symmetric", contrast.contrast_ratio("#123456", "#fedcba")
                              == contrast.contrast_ratio("#fedcba", "#123456"))
    check("rounding never rounds a fail up to the bar",
          contrast.round_ratio(4.4999) == 4.4, f"got {contrast.round_ratio(4.4999)}")
    check("large text starts at 24px (18pt) regular", contrast.is_large_text(24.0, False) and not contrast.is_large_text(23.99, False))
    check("large bold text starts at 18.67px (14pt)", contrast.is_large_text(18.67, True) and not contrast.is_large_text(18.66, True))

# ------------------------------------------------------------- MUTATION
def gate_mutation():
    gate("MUTATION: each rule must go red on input built to break it")
    MUTANTS = {
        "1.4.3 normal text below 4.5:1": {"id": "m", "fg": "#777777", "bg": "#ffffff", "font_px": 16, "kind": "text"},
        "1.4.3 large text below 3:1":    {"id": "m", "fg": "#bbbbbb", "bg": "#ffffff", "font_px": 32, "kind": "text"},
        "1.4.11 non-text below 3:1":     {"id": "m", "fg": "#dddddd", "bg": "#ffffff", "kind": "nontext"},
    }
    for label, el in MUTANTS.items():
        fs = aa(el)
        check(f"{label} -> FAIL", any(f.verdict == "FAIL" for f in fs), f"got {[f.verdict for f in fs]}")
    pair = {"fg": "#949494", "bg": "#ffffff", "kind": "text"}
    small = aa({**pair, "id": "s", "font_px": 16})[0]
    large = aa({**pair, "id": "l", "font_px": 32})[0]
    check("large-text exception actually changes the verdict",
          small.verdict == "FAIL" and large.verdict == "PASS", f"16px={small.verdict} 32px={large.verdict}")
    # Severity must discriminate, and the boundary is two thirds as rules.md says.
    check("severity separates a near miss from unreadable", audit._severity(4.0, 4.5) != audit._severity(1.5, 4.5))
    check("exactly two thirds of the bar is major, not blocker", audit._severity(3.0, 4.5) == "major", audit._severity(3.0, 4.5))
    check("just under two thirds is blocker", audit._severity(2.9, 4.5) == "blocker")
    # Stylesheet-shaped input. The same violation as a stylesheet would hand it over;
    # the conversion happens in code, never in the model that extracted it.
    pt = aa({**pair, "id": "pt", "font_pt": 18})[0]
    px = aa({**pair, "id": "px", "font_px": 18})[0]
    check("font_pt 18 is large text (24px), font_px 18 is not", pt.verdict == "PASS" and px.verdict == "FAIL",
          f"pt={pt.verdict} px={px.verdict}")
    w600 = aa({**pair, "id": "w6", "font_px": 19, "font_weight": 600})[0]
    w700 = aa({**pair, "id": "w7", "font_px": 19, "font_weight": 700})[0]
    check("font_weight 700 is bold, 600 is not", w700.verdict == "PASS" and w600.verdict == "FAIL",
          f"600={w600.verdict} 700={w700.verdict}")
    op = aa({"id": "op", "fg": "#000000", "bg": "#ffffff", "font_px": 16, "opacity": 0.5, "kind": "text"})[0]
    check("opacity below 1 is refused, not measured", op.verdict == "UNDECIDABLE", op.verdict)
    # The standard's exceptions: only when named, and quoting the clause.
    logo = audit.check_element({"id": "logo", "fg": "#eeeeee", "bg": "#ffffff", "font_px": 16, "kind": "text", "exempt": "logotype"})[0]
    check("named logotype is N/A and quotes the Logotypes clause", logo.verdict == "N/A" and "logo or brand name" in logo.quote)
    unnamed = aa({"id": "logo", "fg": "#eeeeee", "bg": "#ffffff", "font_px": 16, "kind": "text"})[0]
    check("the same pair without the exemption named is FAIL", unnamed.verdict == "FAIL")
    bogus = audit.check_element({"id": "x", "fg": "#eeeeee", "bg": "#ffffff", "kind": "nontext", "exempt": "logotype"})[0]
    check("an exemption the criterion does not have is refused", bogus.verdict == "UNDECIDABLE")
    nt = aa({"id": "nt", "fg": "rgba(0,0,0,0.5)", "bg": "#fff", "kind": "nontext"})[0]
    check("an undecidable non-text element cites 1.4.11, not 1.4.3", nt.criterion == "1.4.11", nt.criterion)

# -------------------------------------------------------------- SILENCE
def gate_silence():
    gate("SILENCE: compliant input must produce no AA failures, and passes are reported")
    rep = audit.audit(json.loads((ROOT / "fixtures/clean.json").read_text()))
    check("clean fixture returns verdict PASS", rep["verdict"] == "PASS", rep["verdict"])
    check("clean fixture invents zero failures", rep["summary"]["aa_fail"] == 0, str(rep["summary"]))
    check("clean fixture reports every pass", rep["summary"]["aa_pass"] == rep["summary"]["elements"])
    rep2 = audit.audit(json.loads((ROOT / "fixtures/violating.json").read_text()))
    check("violating fixture returns verdict FAIL", rep2["verdict"] == "FAIL", rep2["verdict"])
    rendered = audit.render(rep2)
    check("an AAA miss is never printed as [FAIL]",
          not any(l.startswith("[FAIL]") and "(AAA)" in l for l in rendered.splitlines()))
    check("an AAA miss is printed as headroom", any(l.startswith("[aaa ]") for l in rendered.splitlines()))
    inc = audit.audit([{"id": "x", "fg": "#767676", "bg": "#fff", "kind": "text"}])
    check("an undecided audit is INCOMPLETE, exit 2, never a silent pass", inc["verdict"] == "INCOMPLETE" and audit.EXIT["INCOMPLETE"] == 2)

# ----------------------------------------------------------- INVARIANCE
def gate_invariance():
    gate("INVARIANCE: one violation, five spellings, five identical verdicts")
    SAME = [
        {"id": "hex6",  "fg": "#777777",            "bg": "#ffffff",          "font_px": 16, "kind": "text"},
        {"id": "hex3",  "fg": "#777",               "bg": "#fff",             "font_px": 16, "kind": "text"},
        {"id": "upper", "fg": "#777777".upper(),    "bg": "#FFFFFF",          "font_px": 16, "kind": "text"},
        {"id": "rgb",   "fg": "rgb(119, 119, 119)", "bg": "rgb(255,255,255)", "font_px": 16, "kind": "text"},
        {"id": "rgba1", "fg": "rgba(119,119,119,1)","bg": "white",            "font_px": 16, "kind": "text"},
    ]
    verdicts, ratios = [], []
    for el in SAME:
        f = aa(el)[0]; verdicts.append(f.verdict); ratios.append(f.measured)
    check("all five spellings produce the same verdict", len(set(verdicts)) == 1, str(verdicts))
    check("all five spellings produce the same ratio", len(set(ratios)) == 1, str(ratios))
    check("and that shared verdict is FAIL", verdicts[0] == "FAIL", verdicts[0])

# --------------------------------------------------------------- PURITY
BANNED = {"requests", "urllib", "httpx", "socket", "http", "openai", "anthropic", "random",
          "aiohttp", "subprocess", "boto3", "os", "importlib", "ssl", "ftplib", "smtplib"}
def gate_purity():
    gate("PURITY: the deterministic layer reaches nothing outside itself")
    for src in ["auditor/checker/contrast.py", "auditor/checker/audit.py", "auditor/checker/findings.py"]:
        tree = ast.parse((ROOT / src).read_text())
        found, dyn = set(), False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("__import__", "eval", "exec"):
                dyn = True
        check(f"{src} imports nothing that reaches out", not (found & BANNED), f"found {found & BANNED}")
        check(f"{src} has no dynamic import or eval", not dyn)

# ------------------------------------------------------------- CITATION
def gate_citation():
    gate("CITATION: every finding names a real provision, quotes it verbatim, and recomputes")
    own = audit.render(audit.audit(json.loads((ROOT / "fixtures/violating.json").read_text())))
    parsed = findings.parse_findings(own)
    check("the checker's own output parses back", len(parsed) == 6, str(len(parsed)))
    rejected = [(f["location"], findings.citation_gate(f)) for f in parsed if findings.citation_gate(f)]
    check("the checker's own output passes its own gate", not rejected, str(rejected))
    broken = (ROOT / "examples/findings-broken.md").read_text()
    results = {f["location"]: findings.citation_gate(f) for f in findings.parse_findings(broken)}
    check("examples/findings-broken.md parses to four findings", len(results) == 4, str(len(results)))
    check("the valid finding holds", results.get("muted caption") == [], str(results.get("muted caption")))
    print("\n  --- DEMONSTRATION: the citation gate, fired on purpose")
    caught = {}
    for loc, codes in results.items():
        for c in codes:
            print(f"      caught: {loc}: {c}")
            caught.setdefault(loc, set()).add(c.split("_")[0])
    check("planted nonexistent SC is caught by check A", "A" in caught.get("orange CTA text", set()))
    check("planted non-verbatim quote is caught by check C", "C" in caught.get("ghost border", set()))
    check("planted wrong-kind criterion is caught by check D", "D" in caught.get("no size given", set()))
    check("exactly three of four findings rejected", len(caught) == 3, str(sorted(caught)))

# -------------------------------------------------------------- EXAMPLES
FENCE = re.compile(r"```text (excerpt )?fixture=(\S+)\n(.*?)\n```", re.S)
def gate_examples():
    gate("EXAMPLES: every pasted output in examples.md is a live run of the checker")
    text = (AUDITOR / "examples.md").read_text()
    blocks = FENCE.findall(text)
    check("examples.md carries at least three tagged output blocks", len(blocks) >= 3, str(len(blocks)))
    for excerpt, fixture, body in blocks:
        rep = audit.render(audit.audit(json.loads((ROOT / fixture).read_text())))
        if excerpt:
            check(f"excerpt of {fixture} appears verbatim in a live run", body.strip() in rep)
        else:
            check(f"full output for {fixture} equals a live run byte for byte", body.strip() == rep.strip())

# -------------------------------------------------------------- runner
def verify_reference() -> int:
    m = json.loads((REF / "MANIFEST.json").read_text())
    print(f"source:  {m['source']}\nstatus:  {m['status']}\nfetched: {m['fetched_utc']}\npage sha256: {m['source_sha256']}\n")
    for group in ("criteria", "definitions"):
        for key, v in m[group].items():
            print(f"  {group[:-1]:10} {key:18} {v['file']:44} {v['sha256'][:12]}")
    return 0

def main(argv: list[str]) -> int:
    if argv[1:] == ["--verify-reference"]:
        return verify_reference()
    if len(argv) == 2:
        return _cite_only(argv[1])
    for g in (gate_shape, gate_provenance, gate_anchor, gate_mutation, gate_silence,
              gate_invariance, gate_purity, gate_citation, gate_examples):
        g()
    print("\n" + "=" * 62)
    print(f"{COUNT} checks in {GATES} gates: {COUNT - len(FAILS)} passed, {len(FAILS)} failed")
    if FAILS:
        for f in FAILS: print(f"  - {f}")
        print("GATE FAILED"); return 1
    print("GATE PASSED: every rule was shown to fail on purpose, stay quiet on compliant")
    print("input, hold across five spellings, cite only what is on disk, and recompute.")
    return 0

def _cite_only(path: str) -> int:
    sys.argv = ["findings.py", path]
    return findings.main()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
