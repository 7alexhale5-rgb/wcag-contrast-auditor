"""Offline regressions for UTF-8 text and exact reference bytes on every OS."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check


@contextlib.contextmanager
def windows_text_defaults():
    """Emulate legacy Windows file defaults without changing the host locale."""
    original = io.open

    def windows_open(
        file,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        if "b" not in mode:
            if encoding in (None, "locale"):
                encoding = "cp1252"
            if newline is None and any(flag in mode for flag in "wax"):
                newline = "\r\n"
        return original(
            file, mode, buffering, encoding, errors, newline, closefd, opener
        )

    with patch("io.open", windows_open):
        yield


class PortabilityTests(unittest.TestCase):
    def test_all_existing_gates_with_windows_default_encoding(self):
        with (
            windows_text_defaults(),
            contextlib.redirect_stdout(io.StringIO()),
            patch.object(check, "FAILS", []),
            patch.object(check, "COUNT", 0),
            patch.object(check, "GATES", 0),
        ):
            self.assertEqual(check.main(["check.py"]), 0)

    def test_audit_reads_utf8_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_bytes(
                json.dumps(
                    [
                        {
                            "id": "Copyright © – 日本語",
                            "fg": "#000",
                            "bg": "#fff",
                            "font_px": 16,
                        }
                    ],
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            output = io.StringIO()
            with (
                windows_text_defaults(),
                patch.object(sys, "argv", ["audit.py", str(source)]),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(check.audit.main(), 0)
            self.assertIn("Copyright © – 日本語", output.getvalue())

    def test_findings_reads_utf8_report_and_notices(self):
        report = check.audit.render(
            check.audit.audit(
                [
                    {
                        "id": "Copyright © – 日本語",
                        "fg": "#000",
                        "bg": "#fff",
                        "font_px": 16,
                    },
                ]
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.md"
            source.write_bytes(report.encode("utf-8"))
            output = io.StringIO()
            with (
                windows_text_defaults(),
                patch.object(sys, "argv", ["findings.py", str(source)]),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(check.findings.main(), 0)
            self.assertIn("Copyright © – 日本語", output.getvalue())

    def test_both_reference_gates_reject_changed_line_ending_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp)
            for source in check.REF.iterdir():
                if source.suffix in (".md", ".json"):
                    (ref / source.name).write_bytes(source.read_bytes())
            self.assertEqual(check.findings.verify_reference(ref), [])
            source = ref / "wcag21-1.4.3.md"
            source.write_bytes(source.read_bytes().replace(b"\n", b"\r\n"))
            self.assertTrue(check.findings.verify_reference(ref))
            with (
                patch.object(check, "REF", ref),
                patch.object(check, "FAILS", []),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                check.gate_provenance()
                self.assertIn("1.4.3: file hash matches the manifest", check.FAILS)

    def test_fetch_writes_utf8_lf_bytes_matching_manifest(self):
        spec = importlib.util.spec_from_file_location(
            "fetch_standard", check.REF / "fetch-standard.py"
        )
        fetch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetch)
        notice = "Copyright © – 日本語"
        html = (
            '<p id="w3c-state">W3C Recommendation</p><p class="copyright">'
            + notice
            + "</p>"
        )
        html += "".join(
            f'<section id="{key}"><p>Required text.</p></section>'
            for key in fetch.WANTED
        )
        html += "".join(
            f'<dt><dfn id="{key}">Term</dfn></dt><dd>Defined text.</dd>'
            for key in fetch.DFNS
        )
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp)
            with (
                patch.object(fetch, "HERE", ref),
                patch.object(
                    fetch.urllib.request,
                    "urlopen",
                    return_value=io.BytesIO(html.encode("utf-8")),
                ),
                windows_text_defaults(),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(fetch.main(), 0)
            manifest = json.loads((ref / "MANIFEST.json").read_bytes().decode("utf-8"))
            for group in ("criteria", "definitions"):
                for entry in manifest[group].values():
                    raw = (ref / entry["file"]).read_bytes()
                    self.assertNotIn(b"\r", raw)
                    self.assertIn(notice, raw.decode("utf-8"))
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
            self.assertNotIn(b"\r", (ref / "MANIFEST.json").read_bytes())
            self.assertEqual(check.findings.verify_reference(ref), [])


if __name__ == "__main__":
    unittest.main()
