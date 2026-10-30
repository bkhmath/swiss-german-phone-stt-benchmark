"""Canonicalise numbers in Standard German text so that "75'000", "75 000" and
"fünfundsiebzigtausend" all become 75000, and "drei" == "3".

Conventions (applied identically to reference and hypothesis):
- Swiss/German thousand separators (', ’, .) inside a single token are removed.
- Other non-digit characters split a number: "01.01.2021" -> 1, 1, 2021; "1,5" -> 1, 5.
- Scale words (Mio., Millionen, Mrd., Milliarden) are dropped: "50 Mio." == "fünfzig Millionen" -> 50.
- The article "ein/eine/einen/..." is not a number; "eins" is.
- Ordinal words ("zweite") are ignored; ordinal digits ("12.") count as 12.
"""
import re
import unicodedata

_BASIC = {
    "null": 0, "eins": 1, "ein": 1, "zwei": 2, "zwo": 2, "drei": 3, "vier": 4,
    "fünf": 5, "sechs": 6, "sieben": 7, "acht": 8, "neun": 9, "zehn": 10,
    "elf": 11, "zwölf": 12, "dreizehn": 13, "vierzehn": 14, "fünfzehn": 15,
    "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19,
    "zwanzig": 20, "dreissig": 30, "vierzig": 40, "fünfzig": 50,
    "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90,
}
_SCALES = [("tausend", 1000), ("hundert", 100)]
_ARTICLES = {"ein", "eine", "einen", "einem", "einer", "eines"}
_GROUPED = re.compile(r"(?<![\d.,'’])\d{1,3}(?:(?:'|’|\.)\d{3})+(?![\d'’]|\.\d)")
_WORD = re.compile(r"[a-zäöüß]+|\d+")


def _parse_word(w: str):
    if not w:
        return None
    if w in _BASIC:
        return _BASIC[w]
    for name, val in _SCALES:
        if name in w:
            left, right = w.split(name, 1)
            lv = _parse_word(left) if left else 1
            rv = _parse_word(right) if right else 0
            if lv is None or rv is None or lv >= val or (right and rv >= val):
                return None
            return lv * val + rv
    if "und" in w:
        a, b = w.split("und", 1)
        av, bv = _parse_word(a), _parse_word(b)
        if av is not None and bv is not None and 1 <= av <= 9 and bv in range(20, 100, 10):
            return av + bv
    return None


def _prep(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower().replace("ß", "ss")
    # remove thousand separators inside grouped numbers: 75'000 -> 75000
    return _GROUPED.sub(lambda m: re.sub(r"['’.]", "", m.group()), text)


def tokens(text: str) -> list[str]:
    """Lowercased word tokens with every number rewritten as its integer value."""
    out = []
    for tok in _WORD.findall(_prep(text)):
        if tok.isdigit():
            out.append(str(int(tok)))
        elif tok not in _ARTICLES and (v := _parse_word(tok)) is not None:
            out.append(str(v))
        elif tok.endswith("mal") and (v := _parse_word(tok[:-3])) is not None and v >= 2:
            out += [str(v), "mal"]  # "zweimal" == "zwei Mal"; "einmal" stays an adverb
        else:
            out.append(tok)
    return out


def numbers(text: str) -> list[int]:
    return [int(t) for t in tokens(text) if t.isdigit()]
