#!/usr/bin/env python3
"""Fetch the normative WCAG 2.1 success criteria this auditor cites, straight from w3.org.

Why this exists: a finding that cites a criterion is only checkable if the auditor also
holds the text it read. This script re-derives reference/ from source so any reader can
confirm the copy in this repo matches the published Recommendation, and see the date it
was taken. Run it, then `git diff reference/` to see whether the standard moved.
"""
import hashlib, json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser

SRC = "https://www.w3.org/TR/WCAG21/"
HERE = Path(__file__).resolve().parent
# Criteria this auditor enforces. Keep this list in sync with checker/rules.
WANTED = {
    "contrast-minimum":     "1.4.3",
    "non-text-contrast":    "1.4.11",
    "contrast-enhanced":    "1.4.6",
}

class Section(HTMLParser):
    """Pull the <section id=...> blocks we care about, as plain text."""
    def __init__(self, ids):
        super().__init__(); self.ids=ids; self.depth=0; self.cur=None
        self.out={}; self.buf=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="section":
            if self.cur is not None: self.depth+=1
            elif a.get("id") in self.ids: self.cur=a["id"]; self.depth=1; self.buf=[]
        if self.cur and tag in ("script","style"): self.skip+=1
        if self.cur and tag in ("p","li","dt","dd","h1","h2","h3","h4"): self.buf.append("\n")
        if self.cur and tag=="li": self.buf.append("- ")
    def handle_endtag(self, tag):
        if self.cur and tag in ("script","style") and self.skip: self.skip-=1
        if tag=="section" and self.cur is not None:
            self.depth-=1
            if self.depth==0:
                self.out[self.cur]="".join(self.buf); self.cur=None
    def handle_data(self, d):
        if self.cur and not self.skip: self.buf.append(d)

def tidy(t):
    t=re.sub(r"[ \t]+"," ",t)
    t=re.sub(r"\n\s*\n\s*\n+","\n\n",t)
    return "\n".join(l.rstrip() for l in t.strip().splitlines())

def main():
    raw=urllib.request.urlopen(SRC, timeout=60).read()
    sha=hashlib.sha256(raw).hexdigest()
    fetched=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p=Section(set(WANTED)); p.feed(raw.decode("utf-8","replace"))
    missing=[k for k in WANTED if k not in p.out]
    if missing:
        print(f"FAIL: could not locate section(s) {missing} at {SRC}", file=sys.stderr); return 1
    manifest={"source":SRC,"fetched_utc":fetched,"source_sha256":sha,"criteria":{}}
    for sid,num in WANTED.items():
        body=tidy(p.out[sid])
        doc=(f"# WCAG 2.1 Success Criterion {num}\n\n"
             f"Source: {SRC}#{sid}\n"
             f"Retrieved (UTC): {fetched}\n"
             f"SHA-256 of the full source document at retrieval: {sha}\n\n"
             "Reproduced under the W3C Document License. Copyright (c) W3C(R) (MIT, ERCIM,\n"
             "Keio, Beihang). https://www.w3.org/copyright/document-license/\n"
             "This is a verbatim excerpt of the normative text. If it disagrees with the\n"
             "published Recommendation, the Recommendation governs.\n\n"
             "---\n\n"+body+"\n")
        out=HERE/f"wcag21-{num}.md"; out.write_text(doc)
        manifest["criteria"][num]={"section_id":sid,"file":out.name,
                                   "sha256":hashlib.sha256(doc.encode()).hexdigest()}
        print(f"wrote {out.name}  ({len(body)} chars)")
    (HERE/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"wrote MANIFEST.json  (source sha256 {sha[:16]}...)")
    return 0

if __name__=="__main__":
    sys.exit(main())
