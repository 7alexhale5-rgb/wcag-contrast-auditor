#!/usr/bin/env python3
"""Build real-territory fixtures from public design-token files. Run once; output is committed.

Source: DESIGN.md files copied from the VoltAgent awesome-design-md catalog
(https://github.com/VoltAgent/awesome-design-md). Only files whose provenance
block names that catalog are used; anything else in the local pool is skipped,
so no private or client token file can reach this public repo.

Each token file has a YAML front matter with a `colors:` map and a `typography:`
map. Role names vary by brand, so the pairing below is explicit and published:
the auditor is only as honest as the pairing rule, and a reader should be able
to disagree with it. `border`, `hairline` and `muted` carry notes because the
schema does not say whether they outline a control or divide a page, and the
independent oracle (software-factory design_check.py) records the same caveat.

font size comes from typography.body-md.fontSize, then body.fontSize. If neither
exists the element carries no font_px and the checker returns UNDECIDABLE. It is
never assumed to be 16.

Every element records xref_ratio: the ratio computed by a second, independent
WCAG implementation (the oracle) at build time, so check.py can replay the
differential offline.
"""
import json, re, sys, hashlib, datetime
from pathlib import Path

POOL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Projects/design-vault/brand-systems"
ORACLE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Projects/software-factory/bin/design_check.py"
OUT = Path(__file__).resolve().parent / "brands"
RECEIPT = Path(__file__).resolve().parent.parent / "receipts" / "EXPECTED-brands.json"
# Pinned to one upstream commit so the source a fixture names can be opened and
# hashed by anyone. The local copy is compared to the upstream file at build time.
UPSTREAM_COMMIT = "8147538b4226ae41e2487a9179e3bcc1f68e8554"   # main on 2026-07-31
UPSTREAM = "https://github.com/VoltAgent/awesome-design-md/blob/" + UPSTREAM_COMMIT + "/design-md/{slug}/DESIGN.md"
UPSTREAM_RAW = "https://raw.githubusercontent.com/VoltAgent/awesome-design-md/" + UPSTREAM_COMMIT + "/design-md/{slug}/DESIGN.md"

TEXT_PAIRS = [("foreground", "background"), ("primary-foreground", "primary"), ("on-primary", "primary"),
              ("ink", "canvas"), ("body", "canvas"), ("muted", "canvas"), ("muted-foreground", "background")]
NONTEXT_PAIRS = [("ring", "background"), ("border", "background"), ("hairline", "canvas"), ("border", "canvas")]
NOTES = {
    "border": "ambiguous role: a page divider is out of scope for 1.4.11, a control outline is in scope; the oracle warns rather than fails on this pair",
    "hairline": "ambiguous role: a page divider is out of scope for 1.4.11, a control outline is in scope; the oracle warns rather than fails on this pair",
    "muted": "the oracle skips this pair because some schemas use muted as a surface, not text; included here as text on the reading that muted is muted text",
}

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auditor/checker"))
import contrast, audit  # noqa: E402
import yaml  # noqa: E402  (PyYAML; only the builder needs it, never the auditor)

def load_oracle():
    import importlib.util
    spec = importlib.util.spec_from_file_location("design_check", ORACLE)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def frontmatter(text: str) -> dict | None:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m: return None
    try: return yaml.safe_load(m.group(1))
    except Exception: return None

def body_px(doc: dict):
    typ = doc.get("typography") or {}
    for key in ("body-md", "body", "text-base", "body-base"):
        v = typ.get(key)
        if isinstance(v, dict) and "fontSize" in v:
            m = re.match(r"([\d.]+)\s*(px|pt|rem)?", str(v["fontSize"]))
            if m:
                n, unit = float(m.group(1)), (m.group(2) or "px")
                return {"px": n, "pt": n * 4 / 3, "rem": n * 16}[unit]
    return None

def upstream_name(text: str, slug: str) -> str:
    """The catalog directory this local copy names in its own provenance line.
    Local slugs were normalised (claude became anthropic, x.ai became xai), so
    the provenance line, not the slug, is the source of truth."""
    m = re.search(r"awesome-design-md/blob/\w+/design-md/([^/\s\"]+)/DESIGN\.md", text)
    return m.group(1) if m else slug

def upstream_body(name: str):
    """The catalog file at the pinned commit, or None if it is not there."""
    import urllib.request, urllib.error
    try:
        return urllib.request.urlopen(UPSTREAM_RAW.format(slug=name), timeout=30).read().decode("utf-8", "replace")
    except urllib.error.HTTPError:
        return None

def colors_of(text: str) -> dict:
    doc = frontmatter(text) or {}
    return {str(k): str(v) for k, v in (doc.get("colors") or {}).items()} if isinstance(doc.get("colors"), dict) else {}

def main() -> int:
    oracle = load_oracle()
    OUT.mkdir(exist_ok=True)
    expected, skipped, built = {}, [], 0
    for path in sorted(POOL.glob("*/DESIGN.md")):
        slug = path.parent.name
        text = path.read_text()
        if "VoltAgent" not in text:
            skipped.append((slug, "no catalog provenance")); continue
        doc = frontmatter(text)
        if not doc or not isinstance(doc.get("colors"), dict):
            skipped.append((slug, "front matter did not parse")); continue
        colors = {str(k): str(v) for k, v in doc["colors"].items()}
        px = body_px(doc)
        elements = []
        for fg, bg in TEXT_PAIRS:
            if fg in colors and bg in colors:
                el = {"id": f"{fg} on {bg}", "fg": colors[fg], "bg": colors[bg], "kind": "text"}
                if px is not None: el["font_px"] = px
                if fg in NOTES: el["note"] = NOTES[fg]
                elements.append(el)
        for fg, bg in NONTEXT_PAIRS:
            if fg in colors and bg in colors:
                el = {"id": f"{fg} on {bg}", "fg": colors[fg], "bg": colors[bg], "kind": "nontext"}
                if fg in NOTES: el["note"] = NOTES[fg]
                elements.append(el)
        if not elements:
            skipped.append((slug, "no recognised role pairs")); continue
        for el in elements:
            r = oracle.contrast_ratio(el["fg"], el["bg"]) if re.fullmatch(r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}", el["fg"]) and re.fullmatch(r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}", el["bg"]) else None
            el["xref_ratio"] = round(r, 2) if r is not None else None
        name = upstream_name(text, slug)
        up = upstream_body(name)
        if up is None:
            skipped.append((slug, f"not in the catalog at the pinned commit as design-md/{name}")); continue
        fixture = {"brand": slug, "source": UPSTREAM.format(slug=name),
                   "upstream_commit": UPSTREAM_COMMIT,
                   "upstream_sha256": hashlib.sha256(up.encode()).hexdigest() if up is not None else None,
                   "upstream_colors_match_local": (colors_of(up) == colors) if up is not None else None,
                   "extracted": datetime.date.today().isoformat(),
                   "pairing_rule": "fixtures/build_brand_fixtures.py TEXT_PAIRS and NONTEXT_PAIRS",
                   "elements": elements}
        (OUT / f"{slug}.json").write_text(json.dumps(fixture, indent=2) + "\n")
        rep = audit.audit(elements)
        expected[slug] = {"verdict": rep["verdict"],
                          "findings": [[f["location"], f["criterion"], f["level"], f["verdict"], f["measured"]]
                                       for f in rep["findings"]]}
        built += 1
    RECEIPT.parent.mkdir(exist_ok=True)
    anchors = json.loads(RECEIPT.read_text()).get("hand_anchors", []) if RECEIPT.exists() else []
    RECEIPT.write_text(json.dumps({"generated": datetime.date.today().isoformat(),
                                   "note": "verdicts generated by auditor/checker/audit.py at build time; five pairs were also checked by hand against WebAIM before this file was trusted (see hand_anchors)",
                                   "hand_anchors": anchors, "brands": expected}, indent=2) + "\n")
    print(f"built {built} fixtures; skipped {len(skipped)}")
    for s, why in skipped: print(f"  skip {s}: {why}")
    verdicts = {}
    for s, e in expected.items(): verdicts[e["verdict"]] = verdicts.get(e["verdict"], 0) + 1
    print("verdicts:", verdicts)
    return 0

if __name__ == "__main__":
    sys.exit(main())
