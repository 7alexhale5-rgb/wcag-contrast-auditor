"""Input and numeric regressions; no network or third-party dependencies."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "auditor" / "checker"))
import audit
import contrast

BASE = {"id": "sample", "fg": "#000", "bg": "#fff", "font_px": 16}


class InputTests(unittest.TestCase):
    def assert_unknown(self, changes):
        findings = audit.check_element({**BASE, **changes})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].verdict, "UNDECIDABLE")
        self.assertIsNone(findings[0].measured)

    def test_bold_requires_boolean(self):
        for value in ("false", "true", 0, 1, None, [], {}):
            with self.subTest(value=value):
                self.assert_unknown({"bold": value})
        for value in (False, True):
            self.assertEqual(audit.normalise({**BASE, "bold": value})["bold"], value)

    def test_sizes_require_finite_positive_values_and_matching_units(self):
        bad = (0, -1, math.nan, math.inf, -math.inf, True, False, None,
               "nan", "inf", "0px", "-1px", [], {}, 10 ** 400)
        for key in ("font_px", "font_pt"):
            for value in bad:
                with self.subTest(key=key, value=value):
                    self.assert_unknown({key: value})
        for key, value in (("font_px", "18pt"), ("font_pt", "24px"),
                           ("font_px", "1rem"), ("font_px", "18pxpt")):
            with self.subTest(key=key, value=value):
                self.assert_unknown({key: value})
        self.assertEqual(audit.normalise({"font_px": "24px"})["font_px"], 24)
        self.assertEqual(audit.normalise({"font_pt": "18pt"})["font_px"], 24)
        self.assertEqual(audit.normalise({"font_px": " 24 "})["font_px"], 24)

    def test_dual_sizes_agree_or_are_rejected(self):
        for px, pt in ((24, 18), ("24px", "18pt"), (20, 15), (56 / 3, 14), ("19.2px", "14.4pt")):
            with self.subTest(px=px, pt=pt):
                self.assertEqual(audit.normalise({"font_px": px, "font_pt": pt})["font_px"], float(str(px).removesuffix("px")))
        self.assert_unknown({"font_px": 24, "font_pt": 12})
        self.assert_unknown({"font_px": 24, "font_pt": math.nextafter(18, 0)})

    def test_weight_bounds_and_relative_context(self):
        for value in ("bolder", "lighter", math.inf, -math.inf, math.nan,
                      0, -1, 1001, True, False, None, [], {}, 10 ** 400,
                      "1000.000000000000000000001", "0.999999999999999999999"):
            with self.subTest(value=value):
                self.assert_unknown({"font_weight": value})
                with self.assertRaises(contrast.WeightError):
                    contrast.is_bold(value)
        for value, expected in ((1, False), (699.9, False), (700, True),
                                (1000, True), ("bold", True), ("normal", False),
                                ("699.999999999999999999999", False)):
            self.assertEqual(contrast.is_bold(value), expected)

    def test_dual_weight_declarations_must_agree(self):
        for bold, weight in ((False, 700), (True, 600), (True, "lighter"),
                             (False, "bolder"), (True, math.inf)):
            with self.subTest(bold=bold, weight=weight):
                self.assert_unknown({"bold": bold, "font_weight": weight})
        for bold, weight in ((True, 700), (False, 600), (True, "bold")):
            self.assertEqual(audit.normalise({**BASE, "bold": bold, "font_weight": weight})["bold"], bold)

    def test_exact_large_text_boundaries_in_points_and_pixels(self):
        for pt, bold in ((14, True), (18, False)):
            for size, required in ((pt, 3), (math.nextafter(pt, 0), 4.5),
                                   (math.nextafter(pt, math.inf), 3)):
                with self.subTest(pt=size, bold=bold):
                    finding = audit.check_element({"fg": "#888", "bg": "#fff", "font_pt": size, "bold": bold})[0]
                    self.assertEqual(finding.required, required)
            px = pt * 4 / 3
            for size, expected in ((px, True), (math.nextafter(px, 0), False)):
                self.assertEqual(contrast.is_large_text(size, bold), expected)

    def test_size_precision_cannot_promote_threshold_or_hide_conflict(self):
        cases = (
            {"font_pt": "13.999999999999999999999", "bold": True},
            {"font_pt": "17.999999999999999999999"},
            {"font_px": "23.999999999999999999999"},
            {"font_px": "24.000000000000000000001", "font_pt": 18},
        )
        for fields in cases:
            raw = {"id": "precise", "fg": "#888", "bg": "#fff", **fields}
            with self.subTest(fields=fields):
                rep = audit.audit([raw])
                finding = rep["findings"][0]
                if "font_px" in fields and "font_pt" in fields:
                    self.assertEqual(finding["verdict"], "UNDECIDABLE")
                    self.assertIsNone(finding["measured"])
                    self.assertEqual(finding["input"], raw)
                else:
                    self.assertEqual(finding["verdict"], "FAIL")
                    self.assertEqual(finding["measured"], 3.5)
                self.assertEqual(finding["required"], 4.5)
                self.assertEqual(json.loads(json.dumps(rep)), rep)

    def test_opacity_is_finite_in_range_and_exactly_opaque(self):
        for value in (-1, 0, 0.5, 0.999, math.nextafter(1, 0), 1.001,
                      math.inf, math.nan, True, False, None, "1px", [], {},
                      "0.999999999999999999999", "1.000000000000000000001",
                      "1e-999999999999999999999"):
            with self.subTest(value=value):
                self.assert_unknown({"opacity": value})
        for value in (1, 1.0, "1"):
            self.assertEqual(audit.check_element({**BASE, "opacity": value})[0].verdict, "PASS")

    def test_invalid_elements_are_retained_alongside_valid_elements(self):
        raw = {**BASE, "font_px": "big", "bold": "false"}
        self.assertEqual(audit.check_element(raw)[0].input, raw)
        malformed = [None, [], "text", 7, {**BASE, "kind": "image"},
                     {**BASE, "kind": []}, {**BASE, "fg": 42}]
        rep = audit.audit([BASE, *malformed])
        self.assertEqual(rep["summary"]["aa_pass"], 1)
        self.assertEqual(rep["summary"]["undecidable"], len(malformed))
        self.assertEqual(rep["verdict"], "INCOMPLETE")

    def test_cli_mixed_elements_and_aaa_exit_semantics(self):
        cases = (([BASE], 0, "PASS"), ([BASE, None], 2, "INCOMPLETE"),
                 ([None, {**BASE, "fg": "#777"}, BASE], 1, "FAIL"),
                 ([{**BASE, "fg": "#767676"}], 0, "PASS"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pairs.json"
            for elements, exit_code, verdict in cases:
                path.write_text(json.dumps(elements), encoding="utf-8")
                result = subprocess.run([sys.executable, str(ROOT / "auditor/checker/audit.py"), str(path), "--json"], capture_output=True, text=True, encoding="utf-8")
                with self.subTest(elements=elements):
                    self.assertEqual(result.returncode, exit_code, result.stderr)
                    rep = json.loads(result.stdout)
                    self.assertEqual(rep["verdict"], verdict)
                    if elements == [{**BASE, "fg": "#767676"}]:
                        self.assertIn("[aaa ]", audit.render(rep))
                        self.assertNotIn("[FAIL]", audit.render(rep))


class ColorTests(unittest.TestCase):
    def test_nonstring_colors_raise_named_error(self):
        for value in (None, 42, True, [], {}, (0, 0, 0)):
            with self.subTest(value=value), self.assertRaises(contrast.ColorError):
                contrast.parse_color(value)

    def test_fractional_channels_are_preserved(self):
        for color in ("rgb(1.25, 2.5, 3.75)", "rgb(1.25 2.5 3.75)",
                      "rgba(1.25, 2.5, 3.75, 1)", "rgb(1.25 2.5 3.75 / 100%)"):
            with self.subTest(color=color):
                self.assertEqual(contrast.parse_color(color), (1.25, 2.5, 3.75))

    def test_malformed_or_out_of_range_channels_raise_named_error(self):
        for value in ("rgb(1..2,0,0)", "rgb(.,0,0)", "rgb(255.1,0,0)",
                      "rgb(-0.1,0,0)", "rgb(nan,0,0)", "rgb(inf,0,0)",
                      "rgb(1e999,0,0)", "rgb(1e99999999999999999999,0,0)",
                      "rgb(255.000000000000000000001,0,0)", "rgb(0,,0,0)", "rgb(0,0 0)"):
            with self.subTest(value=value), self.assertRaises(contrast.ColorError):
                contrast.parse_color(value)

    def test_alpha_requires_exactly_one(self):
        for alpha in ("-1", "0", "0.999", "0.9999999999999999", "99.99%",
                      "1.01", "101%", "nan", "inf", "1e999", "1..0", "%",
                      "1e99999999999999999999", "0.999999999999999999999",
                      "1.000000000000000000001"):
            with self.subTest(alpha=alpha), self.assertRaises(contrast.ColorError):
                contrast.parse_color(f"rgba(0,0,0,{alpha})")
        for alpha in ("1", "1.0", "100%"):
            self.assertEqual(contrast.parse_color(f"rgba(0,0,0,{alpha})"), (0, 0, 0))

    def test_fractional_rgb_verdicts_around_both_aa_thresholds(self):
        # Invert the published sRGB luminance formula to generate independent
        # grayscale samples either side of each threshold, far above float noise.
        for threshold, size in ((4.5, 16), (3.0, 24)):
            for ratio, verdict in ((threshold - 0.000001, "FAIL"),
                                   (threshold + 0.000001, "PASS")):
                lum = 1.05 / ratio - 0.05
                channel = 255 * (1.055 * lum ** (1 / 2.4) - 0.055)
                color = f"rgb({channel:.14f}, {channel:.14f}, {channel:.14f})"
                with self.subTest(threshold=threshold, ratio=ratio):
                    self.assertAlmostEqual(contrast.contrast_ratio(color, "#fff"), ratio, places=10)
                    finding = audit.check_element({**BASE, "fg": color, "font_px": size})[0]
                    self.assertEqual(finding.verdict, verdict)


if __name__ == "__main__":
    unittest.main()
