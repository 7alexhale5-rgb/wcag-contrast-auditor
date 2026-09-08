#!/usr/bin/env python3
"""Contrast ratio math, exactly as WCAG 2.1 defines it.

No network. No model. No randomness. Same input, same number, forever.
If this file ever needs an API key, the auditor has stopped being an auditor.
"""
from __future__ import annotations
import math
import re
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

# --- colour parsing ---------------------------------------------------------

_NAMED = {  # the handful that show up in real stylesheets; unknown names raise
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "silver": (192, 192, 192), "navy": (0, 0, 128),
    "teal": (0, 128, 128), "olive": (128, 128, 0), "purple": (128, 0, 128),
    "maroon": (128, 0, 0), "lime": (0, 255, 0), "aqua": (0, 255, 255),
    "fuchsia": (255, 0, 255), "yellow": (255, 255, 0),
}

class ColorError(ValueError):
    pass

def parse_color(value: str) -> tuple[float, float, float]:
    """Accept #rgb, #rrggbb, rgb(), rgba() with opaque alpha, or a named colour."""
    if value is None:
        raise ColorError("no colour given")
    if not isinstance(value, str):
        raise ColorError(f"colour must be a string, got {type(value).__name__}")
    v = value.strip().lower()
    if v in _NAMED:
        return _NAMED[v]
    m = re.fullmatch(r"#([0-9a-f]{3})", v)
    if m:
        return tuple(int(c * 2, 16) for c in m.group(1))  # type: ignore[return-value]
    m = re.fullmatch(r"#([0-9a-f]{6})([0-9a-f]{2})?", v)
    if m:
        h = m.group(1)
        if m.group(2) is not None and int(m.group(2), 16) < 255:
            raise ColorError(f"non-opaque colour {value!r}: composite it before auditing")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    # Keep comma and space syntax separate: repeated or mixed separators are
    # malformed. Channels stay fractional through luminance calculation.
    number = r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:e[+-]?\d+)?"
    channel = f"({number})"
    alpha = f"({number}%?)"
    comma = rf"{channel}\s*,\s*{channel}\s*,\s*{channel}(?:\s*,\s*{alpha})?"
    space = rf"{channel}\s+{channel}\s+{channel}(?:\s*/\s*{alpha})?"
    m = (re.fullmatch(rf"rgba?\(\s*{comma}\s*\)", v)
         or re.fullmatch(rf"rgba?\(\s*{space}\s*\)", v))
    if m:
        a = m.group(4)
        try:
            channels = tuple(Decimal(m.group(i)) for i in (1, 2, 3))
            alpha = Decimal(a.removesuffix("%")) if a is not None else None
        except InvalidOperation:
            raise ColorError(f"invalid numeric colour {value!r}") from None
        if any(not c.is_finite() or not 0 <= c <= 255 for c in channels):
            raise ColorError(f"channel out of range in {value!r}")
        if a is not None:
            # Compare the original decimal, so even 0.999999999999999999999
            # cannot round to an opaque alpha in binary floating point.
            opaque = Decimal(100) if a.endswith("%") else Decimal(1)
            if not alpha.is_finite() or not 0 <= alpha <= opaque:
                raise ColorError(f"alpha out of range in {value!r}")
            if alpha != opaque:
                raise ColorError(f"non-opaque colour {value!r}: composite it before auditing")
        return tuple(float(c) for c in channels)
    raise ColorError(f"unrecognised colour {value!r}")

# --- WCAG relative luminance and contrast ratio -----------------------------
# https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
# https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio

def _channel(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (_channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(fg: str | tuple, bg: str | tuple) -> float:
    a = parse_color(fg) if isinstance(fg, str) else tuple(fg)
    b = parse_color(bg) if isinstance(bg, str) else tuple(bg)
    l1, l2 = relative_luminance(a), relative_luminance(b)
    if l2 > l1:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)

# --- thresholds, quoted from the criteria in reference/ ---------------------

@dataclass(frozen=True)
class Threshold:
    criterion: str      # e.g. "1.4.3"
    level: str          # "AA" or "AAA"
    ratio: float
    applies_to: str
    quote: str          # the requirement, verbatim from the provision file in reference/
    provision_file: str

# Quotes are lifted verbatim from reference/. check.py verifies each one is a
# substring of its file, so a refreshed standard that changes wording goes red here.
AA_NORMAL   = Threshold("1.4.3",  "AA",  4.5, "text under 18pt, or under 14pt bold",
    "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1", "wcag21-1.4.3.md")
AA_LARGE    = Threshold("1.4.3",  "AA",  3.0, "large text: 18pt+, or 14pt+ bold",
    "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1", "wcag21-1.4.3.md")
AA_NONTEXT  = Threshold("1.4.11", "AA",  3.0, "user interface components and graphical objects",
    "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s)", "wcag21-1.4.11.md")
AAA_NORMAL  = Threshold("1.4.6",  "AAA", 7.0, "text under 18pt, or under 14pt bold",
    "The visual presentation of text and images of text has a contrast ratio of at least 7:1", "wcag21-1.4.6.md")
AAA_LARGE   = Threshold("1.4.6",  "AAA", 4.5, "large text: 18pt+, or 14pt+ bold",
    "Large-scale text and images of large-scale text have a contrast ratio of at least 4.5:1", "wcag21-1.4.6.md")

# The standard's own exceptions. An element is exempt only when the input says so
# by name; the auditor never infers that text is a logo. Each maps to the clause
# it quotes, so an N/A verdict is as checkable as a FAIL.
EXEMPTIONS = {
    "text": {
        "logotype":   ("Text that is part of a logo or brand name has no contrast requirement.", "wcag21-1.4.3.md"),
        "incidental": ("Text or images of text that are part of an inactive user interface component, that are pure decoration, that are not visible to anyone, or that are part of a picture that contains significant other visual content, have no contrast requirement.", "wcag21-1.4.3.md"),
    },
    "nontext": {
        "inactive":   ("except for inactive components or where the appearance of the component is determined by the user agent and not modified by the author", "wcag21-1.4.11.md"),
        # A decorative divider is not "required to identify" a component or state,
        # so 1.4.11 does not reach it. The person extracting the element decides
        # that; the auditor only quotes the clause that makes it out of scope.
        "decorative": ("Visual information required to identify user interface components and states", "wcag21-1.4.11.md"),
    },
}
EXEMPTIONS["text"]["inactive"] = EXEMPTIONS["text"]["incidental"]
EXEMPTIONS["text"]["decorative"] = EXEMPTIONS["text"]["incidental"]

# WCAG defines large text in points. CSS px to pt is 1pt = 4/3 px at the
# reference resolution the spec assumes, so 18pt = 24px and 14pt = 18.6667px.
PT_TO_PX = 4 / 3
LARGE_PX = 18 * 4 / 3          # 24.0
LARGE_BOLD_PX = 14 * 4 / 3     # 18.666...

class WeightError(ValueError):
    pass

def is_bold(weight) -> bool:
    """Absolute CSS weights 700..1000 are bold; relative names need context."""
    if isinstance(weight, bool) or not isinstance(weight, (str, int, float)):
        raise WeightError(f"unrecognised font weight {weight!r}")
    w = str(weight).strip().lower()
    if w == "bold": return True
    if w == "normal": return False
    if w in ("bolder", "lighter"):
        raise WeightError(f"relative font weight {weight!r} needs inherited context")
    try:
        number = Decimal(w)
    except InvalidOperation:
        raise WeightError(f"unrecognised font weight {weight!r}") from None
    if not number.is_finite() or not 1 <= number <= 1000:
        raise WeightError(f"font weight must be finite and within 1..1000, got {weight!r}")
    return number >= 700

def is_large_text(font_px: float, bold: bool) -> bool:
    return font_px >= (LARGE_BOLD_PX if bold else LARGE_PX)

def round_ratio(x: float) -> float:
    """One decimal, rounded DOWN, so a 4.4999 never reports as a passing 4.5."""
    return math.floor(x * 10) / 10
