# WCAG 2.1 Glossary: relative luminance

Source: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
Status: W3C Recommendation 06 May 2025
Notice on the source document: Copyright © 2020-2025 World Wide Web Consortium. W3C® liability, trademark and document use rules apply.

Reproduced under the W3C Document License. Copyright (c) W3C(R) (MIT, ERCIM,
Keio, Beihang). https://www.w3.org/copyright/document-license/
This is a verbatim excerpt of the published text. If it disagrees with the
published Recommendation, the Recommendation governs. Retrieval date and the
hash of the full source document are recorded in MANIFEST.json.

---

the relative brightness of any point in a colorspace, normalized to 0 for darkest
 black and 1 for lightest white

 Note 1

For the sRGB colorspace, the relative luminance of a color is defined as L = 0.2126
 * R + 0.7152 * G + 0.0722 * B where R, G and B are defined as:

- if RsRGB <= 0.04045 then R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4

- if GsRGB <= 0.04045 then G = GsRGB/12.92 else G = ((GsRGB+0.055)/1.055) ^ 2.4

- if BsRGB <= 0.04045 then B = BsRGB/12.92 else B = ((BsRGB+0.055)/1.055) ^ 2.4

and RsRGB, GsRGB, and BsRGB are defined as:

- RsRGB = R8bit/255

- GsRGB = G8bit/255

- BsRGB = B8bit/255

The "^" character is the exponentiation operator. (Formula taken from
 [SRGB].)

 Note 2
Before May 2021 the value of 0.04045 in the definition was different (0.03928). It was taken from an older version of the specification and has been updated. It has no practical effect on the calculations in the context of these guidelines.

 Note 3
Almost all systems used today to view web content assume sRGB encoding. Unless it
 is known that another color space will be used to process and display the content,
 authors should evaluate using sRGB colorspace. If using other color spaces, see Understanding Success Criterion 1.4.3.

 Note 4
If dithering occurs after delivery, then the source color value is used. For colors
 that are dithered at the source, the average values of the colors that are dithered
 should be used (average R, average G, and average B).

 Note 5
Tools are available that automatically do the calculations when testing contrast and
 flash.

 Note 6
A separate page giving the relative luminance definition using MathML to display the formulas is available.
