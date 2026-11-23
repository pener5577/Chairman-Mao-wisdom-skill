"""Extract searchable passages from the two printed layouts used by the eight volumes."""

from collections import Counter
from dataclasses import dataclass
import re
import unicodedata

if __package__:
    from .fulltext import FulltextError
else:
    from fulltext import FulltextError


@dataclass
class Line:
    y: float
    left: float
    right: float
    size: float
    font: str
    text: str
    spaced_columns: bool


def _font_name(name):
    # Some PDFs store the GBK family name as a Latin-1 string.
    try:
        return name.encode("latin1").decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def _lines(page, early):
    glyphs = []
    for block in page.get_text("rawdict", flags=0)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                size = span["size"]
                font = _font_name(span["font"])
                for char in span["chars"]:
                    x, y = char["origin"]
                    text = char["c"]
                    if not text.strip() or y < (98 if early else 43) or size >= 30:
                        continue
                    # Raised reference numbers occupy a separate baseline. On the
                    # later plates their numerals and vertical brackets use 小标宋.
                    if size < (8 if early else 5) or ("小标宋" in font and size < 8):
                        continue
                    glyphs.append((y, x, text, round(size, 1), font))
    glyphs.sort(key=lambda glyph: glyph[0])
    offset = 0
    while offset < len(glyphs):
        y = glyphs[offset][0]
        end = offset + 1
        while end < len(glyphs) and glyphs[end][0] - y <= 1.65:
            end += 1
        group = sorted(glyphs[offset:end], key=lambda glyph: glyph[1])
        size, font = Counter((g[3], g[4]) for g in group).most_common(1)[0][0]
        text = "".join(g[2] for g in group)
        # A reference printed above its line can survive font filtering when the
        # title itself is set in large type. Ordinary numeric table cells remain.
        if not re.fullmatch(r"[〔︹\[（(][０-９0-9]+[〕︺\]）)]", text):
            columns = any(r[1] - l[1] > size * 4 for l, r in zip(group, group[1:]))
            yield Line(y, group[0][1], group[-1][1], size, font, text, columns)
        offset = end


def _kind(line, early, in_notes):
    text = line.text
    if text == "注释":
        return "编注"
    if line.spaced_columns or text.isdecimal():
        return "版面"
    body_size = 12.1 if early else 10.1
    song = "SimSun" in line.font or "宋体" in line.font
    if song and abs(line.size - body_size) < 0.65:
        return "正文"
    if in_notes and line.size <= body_size - 1:
        return "编注"
    if line.size <= body_size - 1 and ("SimFang" in line.font or "仿宋" in line.font):
        return "编注"
    return "版面"


def _title_key(text):
    # The later PDFs use a circle glyph for zero that can be absent in the
    # embedded character mapping. This rule is only for checking title alignment.
    text = unicodedata.normalize("NFKC", text).replace("〇", "").replace("○", "")
    return "".join(char for char in text if char.isalnum())


def _work_passages(doc, title, start, stop, early):
    chunks = []
    previous = None
    start_page = end_page = start
    current_kind = None
    in_notes = False
    previous_full = False
    for number in range(start, stop):
        page = doc[number - 1]
        lines = list(_lines(page, early))
        if number == start:
            heading = "".join(line.text for line in lines[:16] if line.size >= (15 if early else 14))
            if _title_key(title.partition("——")[0]) not in _title_key(heading):
                raise FulltextError(f"PDF 第 {start} 页的篇名与《{title}》不符，请核对所用版本。")
        if any("图书在版编目" in line.text for line in lines):
            break
        # The left margin shifts slightly between recto and verso. Short pages
        # sometimes consist entirely of indented lines; fall back to the edition.
        candidates = [line.left for line in lines if (70 <= line.left <= 84 if early else 25 <= line.left <= 45)]
        left = min(candidates, default=78 if early else 35)
        for line in lines:
            if line.text == "注释":
                in_notes = True
            kind = _kind(line, early, in_notes)
            if kind == "正文":
                in_notes = False
            new = (previous is None or kind != current_kind or not previous_full or
                   line.left > left + line.size * 1.1 or kind == "版面" or
                   (number == end_page and line.y - previous.y > 27))
            if new:
                if chunks:
                    yield current_kind, start_page, end_page, "".join(chunks)
                start_page = number
                chunks = []
            elif number != end_page:
                chunks.append("\f" * (number - end_page))
            chunks.append(line.text)
            end_page = number
            previous = line
            current_kind = kind
            previous_full = line.right >= left + (302 if early else 284) - line.size
    if chunks:
        yield current_kind, start_page, end_page, "".join(chunks)


def read_volume(pdf_bytes, items):
    """Yield volume-local work number, text kind, PDF page interval, and text."""
    try:
        import pymupdf
    except ImportError as exc:
        raise FulltextError("解析《毛泽东文集》需要 PyMuPDF，请先运行 python -m pip install PyMuPDF。") from exc
    items = list(items)
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            if not items or not 1 <= items[0][2] <= items[-1][2] <= len(doc):
                raise FulltextError("PDF 页数与目录不符。")
            early = doc[items[0][2] - 1].rect.width > 410
            for index, (number, title, start) in enumerate(items):
                stop = items[index + 1][2] if index + 1 < len(items) else len(doc) + 1
                if stop <= start:
                    raise FulltextError(f"《{title}》的 PDF 页序异常。")
                count = 0
                for kind, first, last, text in _work_passages(doc, title, start, stop, early):
                    yield number, kind, first, last, text
                    count += 1
                if not count:
                    raise FulltextError(f"《{title}》没有可识别的 PDF 文字。")
    except (RuntimeError, ValueError) as exc:
        if isinstance(exc, FulltextError):
            raise
        raise FulltextError(f"无法解析文集 PDF：{exc}") from exc
