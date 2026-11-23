"""Build and search a local, page-addressable index of the eight collected volumes."""

import os
import re
import sqlite3
import tempfile
from bisect import bisect_right
from contextlib import closing
from http.client import HTTPException
from itertools import accumulate
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

if __package__:
    from . import fulltext
else:
    import fulltext


APPLICATION_ID = 0x4D57434C  # MWCL
MAX_PDF_BYTES = 32 * 1024 * 1024
PDF_HOSTS = {"www.cdct.edu.cn", "marxism.suda.edu.cn", "www.hualixy.edu.cn", "mkszy.just.edu.cn"}
KINDS = {"正文", "编注", "版面"}
FulltextError = fulltext.FulltextError


def _check_pdf_url(url):
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.netloc not in PDF_HOSTS or parts.query
            or parts.fragment or not parts.path.lower().endswith(".pdf")):
        raise FulltextError(f"不是目录所用高校的 PDF 地址：{url}")


class _PDFRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _check_pdf_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(url):
    _check_pdf_url(url)
    request = Request(url, headers={"User-Agent": "mao-wisdom/fulltext"})
    opener = build_opener(_PDFRedirect())
    for attempt in range(2):
        try:
            with opener.open(request, timeout=30) as response:
                data = response.read(MAX_PDF_BYTES + 1)
                if len(data) > MAX_PDF_BYTES:
                    raise FulltextError("下载的 PDF 超出单卷大小限制。")
                length = response.headers.get("Content-Length")
                if length and int(length) != len(data):
                    raise FulltextError("PDF 下载不完整。")
                if not data.startswith(b"%PDF-"):
                    raise FulltextError("来源返回的内容不是 PDF。")
                return data
        except HTTPError as exc:
            if attempt or exc.code not in (408, 429, 500, 502, 503, 504):
                raise
        except (TimeoutError, URLError, HTTPException):
            if attempt:
                raise


def _volumes(items):
    volumes = {}
    for volume, number, title, url in items:
        base, fragment = urldefrag(url)
        _check_pdf_url(base)
        match = re.fullmatch(r"page=([1-9]\d*)", fragment)
        if not match or number < 1 or not title:
            raise FulltextError(f"{volume}目录缺少有效篇名、序号或正文首页。")
        start = int(match[1])
        source, contents = volumes.setdefault(volume, (base, []))
        if source != base or number != len(contents) + 1 or (contents and start <= contents[-1][2]):
            raise FulltextError(f"{volume}目录的 PDF 来源、篇目顺序或首页不一致。")
        contents.append((number, title, start))
    if not volumes:
        raise FulltextError("文集目录为空。")
    if len({source for source, _ in volumes.values()}) != len(volumes):
        raise FulltextError("不同卷次指向了同一个 PDF，请核对篇目目录。")
    return volumes


def _write_volume(db, volume, source, contents, fetch, parse):
    work_ids = {}
    for number, title, _ in contents:
        cursor = db.execute("INSERT INTO works(volume, title, url) VALUES (?, ?, ?)",
                            (volume, title, source))
        work_ids[number] = cursor.lastrowid

    for number, kind, start, end, text in parse(fetch(source), contents):
        if (number not in work_ids or kind not in KINDS or start < contents[number - 1][2]
                or end < start or (number < len(contents) and end >= contents[number][2])
                or text.count("\f") != end - start):
            raise FulltextError(f"{volume}第 {number} 篇的段落或分页位置与目录不一致。")
        folded = fulltext._normalized(text)
        if folded:
            db.execute("INSERT INTO paragraphs(work, kind, page, text, folded) VALUES (?, ?, ?, ?, ?)",
                       (work_ids[number], kind, start, text, folded))


def build_index(path, items, *, fetch=None, parse=None):
    """Build from each volume once, replacing the old cache only after a full check."""
    path = Path(path)
    volumes = _volumes(items)
    fulltext._check_target(path, APPLICATION_ID)
    if parse is None:
        # Querying only reads SQLite; verify the optional parser before any fetch.
        try:
            import pymupdf
        except (ImportError, OSError) as exc:
            raise FulltextError(
                "读取《文集》PDF 需要 PyMuPDF。请使用当前 Python 执行 "
                "python -m pip install PyMuPDF，再运行建库命令。"
            ) from exc
        if __package__:
            from .collected_pdf import read_volume
        else:
            from collected_pdf import read_volume
        parse = read_volume
    if fetch is None:
        fetch = _fetch
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".mao-wisdom-", delete=False) as temporary:
        staged = Path(temporary.name)
    try:
        with closing(sqlite3.connect(staged)) as db:
            db.executescript(f"""
                PRAGMA application_id={APPLICATION_ID};
                PRAGMA user_version={fulltext.VERSION};
                CREATE TABLE works (id INTEGER PRIMARY KEY, volume TEXT, title TEXT, url TEXT);
                CREATE TABLE paragraphs (id INTEGER PRIMARY KEY, work INTEGER, kind TEXT,
                                         page INTEGER, text TEXT, folded TEXT);
                CREATE INDEX paragraphs_by_work ON paragraphs(work);
                CREATE TABLE build_info (work_count INTEGER);
            """)
            for volume, (source, contents) in volumes.items():
                try:
                    _write_volume(db, volume, source, contents, fetch, parse)
                except (OSError, HTTPException, ValueError, RuntimeError) as exc:
                    raise FulltextError(f"{volume}下载或解析失败：{exc}") from exc
            count = sum(len(contents) for _, contents in volumes.values())
            db.execute("INSERT INTO build_info VALUES (?)", (count,))
            fulltext._check_index(db, APPLICATION_ID)
            db.commit()
        fulltext._check_target(path, APPLICATION_ID)
        os.replace(staged, path)
    except sqlite3.Error as exc:
        raise FulltextError(f"无法写入文集全文索引：{exc}") from exc
    finally:
        staged.unlink(missing_ok=True)
    return count


def _pages(text, page, position, length):
    if "\f" not in text:
        return page, page
    # SQLite reports zero-based positions here after adjusting instr() below.
    # A page can have zero normalized characters (e.g. punctuation only).
    boundaries = list(accumulate(len(fulltext._normalized(part)) for part in text.split("\f")))
    return (page + bisect_right(boundaries, position),
            page + bisect_right(boundaries, position + length - 1))


def search_index(path, phrase):
    """Yield one hit per passage and point the link to the first matching PDF page."""
    path = Path(path)
    term = fulltext._normalized(phrase)
    if not any(char.isalnum() for char in term):
        raise FulltextError("请输入包含文字或数字的检索词。")
    if not path.is_file():
        raise FulltextError("文集全文索引不存在，请先用 --collection 文集 --build-index 构建。")
    try:
        with closing(fulltext._read_index(path)) as db:
            fulltext._check_index(db, APPLICATION_ID)
            rows = db.execute("""
                SELECT w.volume, w.title, w.url, p.kind, p.page, p.text, instr(p.folded, ?)
                FROM paragraphs p JOIN works w ON w.id = p.work
                WHERE instr(p.folded, ?) > 0 ORDER BY p.work, p.id
            """, (term, term))
            for volume, title, url, kind, page, text, position in rows:
                start, end = _pages(text, page, position - 1, len(term))
                snippet = fulltext._snippet(text, position - 1, len(term)).replace("\f", "")
                yield volume, title, f"{url}#page={start}", start, end, kind, snippet
    except sqlite3.Error as exc:
        raise FulltextError(f"无法读取文集全文索引：{exc}") from exc
