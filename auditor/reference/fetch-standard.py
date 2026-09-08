#!/usr/bin/env python3
"""Fetch the normative WCAG 2.1 text this auditor cites, straight from w3.org.

Why this exists: a finding that cites a criterion is only checkable if the auditor
also holds the text it read. This script re-derives reference/ from source so any
reader can confirm the copy in this repo matches the published Recommendation.

Each provision file carries the URL, the W3C copyright and licence, the document
status, and a SHA-256 of its own extracted text. The retrieval date and the hash of
the whole source page live in MANIFEST.json only, so re-running this on a later
day leaves the provision files byte-identical when the standard has not moved.
That is what makes `git diff reference/*.md` a real currency check.

This is the one script in the repo that touches the network. It is never run by
the auditor or by check.py.
"""
import hashlib, json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser

SRC = "https://www.w3.org/TR/WCAG21/"
HERE = Path(__file__).resolve().parent
# Success criteria this auditor enforces (section id -> criterion number).
WANTED = {
    "contrast-minimum":  "1.4.3",
    "non-text-contrast": "1.4.11",
    "contrast-enhanced": "1.4.6",
}
# Glossary definitions the checker's math and thresholds are read from
# (dfn id -> short name). These live in <dt><dfn id=..>/<dd> pairs, not sections.
DFNS = {
    "dfn-contrast-ratio":      "contrast-ratio",
    "dfn-relative-luminance":  "relative-luminance",
    "dfn-large-scale":         "large-scale-text",
}

class Extract(HTMLParser):
    """Pull wanted <section id> blocks and <dt><dfn id>/<dd> pairs as plain text."""
    def __init__(self, section_ids, dfn_ids):
        super().__init__()
        self.section_ids, self.dfn_ids = section_ids, dfn_ids
        self.cur = None; self.depth = 0; self.buf = []; self.skip = 0
        self.sections = {}; self.dfns = {}
        self.pending_dfn = None; self.in_dd = None; self.status = None; self._in_state = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "p" and a.get("id") == "w3c-state":
            self._in_state = True; self.status = []
        if tag == "section":
            if self.cur is not None: self.depth += 1
            elif a.get("id") in self.section_ids:
                self.cur = a["id"]; self.depth = 1; self.buf = []
        if tag == "dfn" and a.get("id") in self.dfn_ids:
            self.pending_dfn = a["id"]
        if tag == "dd" and self.pending_dfn and self.in_dd is None:
            self.in_dd = self.pending_dfn; self.buf = []
        if (self.cur or self.in_dd) and tag in ("script", "style"): self.skip += 1
        if (self.cur or self.in_dd) and tag in ("p", "li", "dt", "dd", "h1", "h2", "h3", "h4"): self.buf.append("\n")
        if (self.cur or self.in_dd) and tag == "li": self.buf.append("- ")
    def handle_endtag(self, tag):
        if self._in_state and tag == "p": self._in_state = False
        if (self.cur or self.in_dd) and tag in ("script", "style") and self.skip: self.skip -= 1
        if tag == "section" and self.cur is not None:
            self.depth -= 1
            if self.depth == 0:
                self.sections[self.cur] = "".join(self.buf); self.cur = None
        if tag == "dd" and self.in_dd is not None:
            self.dfns[self.in_dd] = "".join(self.buf); self.in_dd = None; self.pending_dfn = None
    def handle_data(self, d):
        if self._in_state: self.status.append(d)
        if (self.cur or self.in_dd) and not self.skip: self.buf.append(d)

def tidy(t):
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return "\n".join(l.rstrip() for l in t.strip().splitlines())

def header(title, anchor, status):
    return (f"# {title}\n\n"
            f"Source: {SRC}#{anchor}\n"
            f"Status: {status}\n\n"
            "Reproduced under the W3C Document License. Copyright (c) W3C(R) (MIT, ERCIM,\n"
            "Keio, Beihang). https://www.w3.org/copyright/document-license/\n"
            "This is a verbatim excerpt of the published text. If it disagrees with the\n"
            "published Recommendation, the Recommendation governs. Retrieval date and the\n"
            "hash of the full source document are recorded in MANIFEST.json.\n\n---\n\n")

def main():
    raw = urllib.request.urlopen(SRC, timeout=60).read()
    page_sha = hashlib.sha256(raw).hexdigest()
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p = Extract(set(WANTED), set(DFNS)); p.feed(raw.decode("utf-8", "replace"))
    status = " ".join("".join(p.status or []).split()) or "status line not found"
    missing = [k for k in WANTED if k not in p.sections] + [k for k in DFNS if k not in p.dfns]
    if missing:
        print(f"FAIL: could not locate {missing} at {SRC}", file=sys.stderr); return 1
    manifest = {"source": SRC, "status": status, "fetched_utc": fetched,
                "source_sha256": page_sha, "criteria": {}, "definitions": {}}
    for sid, num in WANTED.items():
        doc = header(f"WCAG 2.1 Success Criterion {num}", sid, status) + tidy(p.sections[sid]) + "\n"
        out = HERE / f"wcag21-{num}.md"; out.write_text(doc)
        manifest["criteria"][num] = {"section_id": sid, "file": out.name,
                                     "sha256": hashlib.sha256(doc.encode()).hexdigest()}
        print(f"wrote {out.name}")
    for did, name in DFNS.items():
        doc = header(f"WCAG 2.1 Glossary: {name.replace('-', ' ')}", did, status) + tidy(p.dfns[did]) + "\n"
        out = HERE / f"wcag21-glossary-{name}.md"; out.write_text(doc)
        manifest["definitions"][name] = {"dfn_id": did, "file": out.name,
                                         "sha256": hashlib.sha256(doc.encode()).hexdigest()}
        print(f"wrote {out.name}")
    (HERE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote MANIFEST.json  (status: {status}; page sha256 {page_sha[:16]}...)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
