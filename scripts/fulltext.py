"""Build a private, replaceable SQLite index of the catalogued digital editions."""

import os
import re
import sqlite3
import sys
import tempfile
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from html.parser import HTMLParser
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _default_index():
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
        if not root.is_absolute():
            root = Path.home() / ".cache"
    return root / "mao-wisdom" / "fulltext.sqlite3"


DEFAULT_INDEX = _default_index()
APPLICATION_ID = 0x4D575346  # MWSF
POETRY_ID = 0x4D575350
VERSION = 1
MAX_BYTES = 3 * 1024 * 1024
BLOCKS = {"p", "div", "blockquote", "br", "li", "td", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}
DATE = re.compile(r"^[（(]\s*(?:[一二三四五六七八九〇○零\d]{4}年|\d{4}[.．])")
SOURCE = re.compile(r"^[（(]\s*《毛泽东选集》.*人民出版社")
# Signed editorial insertions can also occur inside a body paragraph.
ARCHIVE_NOTE = re.compile(r"〔注[：:][^〔〕]*?——中文马克思主义文库〕")
ARTICLE_URL = re.compile(r"https://www\.marxists\.org/chinese/maozedong/[A-Za-z0-9_.-]+\.html?\Z")
POEM_URL = re.compile(r"https://mooc1\.chaoxing\.com/mooc-ans/ztnodedetailcontroller/visitnodedetail\?[\w=&%-]+\Z")
DABODI_URL = "https://www.12371.gov.cn/h5/article/1438671217310003200/h5/content_1438671217310003200.html"
POEM_WITH_GAP = "七古·送纵宇一郎东行"
GAP_REFERENCE = "https://cpc.people.com.cn/GB/68742/69115/69120/5282691.html"


class FulltextError(ValueError):
    """An unsuitable page, search query or cache."""


class _Article(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.after_navigation = False
        self.body_started = False
        self.done = False
        self.skip = None
        self.date_field = False
        self.parts = []
        self.paragraphs = []

    def flush(self):
        text = ARCHIVE_NOTE.sub("", "".join(self.parts)).strip()
        self.parts.clear()
        if not text:
            return
        if not self.body_started:
            if self.date_field or DATE.match(text):
                self.body_started = True
            return
        if text.startswith(("*", "＊", "· 附录")) or SOURCE.match(text):
            return
        self.paragraphs.append(text)

    def handle_starttag(self, tag, attrs):
        if self.done or self.skip:
            return
        attrs = dict(attrs)
        if tag == "hr":
            self.flush()
            if self.after_navigation:
                self.done = True
            self.after_navigation = True
            return
        if not self.after_navigation:
            return
        if tag in BLOCKS:
            self.flush()
        if tag == "p":
            self.date_field = "date" in (attrs.get("class") or "").split()
        # The site's prefatory blockquote is an editor's introduction. Later
        # blockquotes include letters and quoted documents in the work itself.
        if (tag in {"script", "style", "sup"} or
                (tag == "a" and (attrs.get("href") or "").startswith("#_ftn")) or
                (tag == "blockquote" and self.body_started and not self.paragraphs)):
            self.skip = tag

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip:
                self.skip = None
            return
        if self.done or not self.after_navigation:
            return
        if tag in BLOCKS or tag == "body":
            self.flush()
        if tag == "p":
            self.date_field = False
        if tag == "body":
            self.done = True

    def handle_data(self, data):
        if self.after_navigation and not self.skip and not self.done:
            self.parts.append(data)


def parse_paragraphs(html):
    parser = _Article()
    parser.feed(html)
    parser.close()
    parser.flush()
    if not parser.body_started or not parser.paragraphs:
        raise FulltextError("网页中没有识别到正文，请核对电子版。")
    return parser.paragraphs


class _VersePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.in_heading = False
        self.heading = []
        self.paragraph = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag == "div":
            if self.depth or attrs.get("id") == "contentDescriptionBox" or "ck-content" in classes:
                self.depth += 1
        if tag == "span" and attrs.get("id") == "nodeTitleEle":
            self.in_heading = True
        if self.depth and tag == "p":
            self.paragraph = (classes, [])

    def handle_endtag(self, tag):
        if tag == "div" and self.depth:
            self.depth -= 1
        if tag == "span":
            self.in_heading = False
        if tag == "p" and self.paragraph is not None:
            classes, chunks = self.paragraph
            self.rows.append((classes, "".join(chunks).strip()))
            self.paragraph = None

    def handle_data(self, data):
        if self.in_heading:
            self.heading.append(data)
        if self.paragraph is not None:
            self.paragraph[1].append(data)


def parse_poems(html, title, url):
    page = _VersePage()
    page.feed(html)
    page.close()
    if url == DABODI_URL:
        # This source quotes both stanzas consecutively, followed by an analysis.
        texts = [text for _, text in page.rows if text]
        for first, second in zip(texts, texts[1:]):
            if (first.startswith("赤橙黄绿青蓝紫") and first.endswith("关山阵阵苍。")
                    and second.startswith("当年鏖战急") and second.endswith("今朝更好看。")):
                return [first + second]
        raise FulltextError("未找到《菩萨蛮·大柏地》的两阕正文。")
    heading = title.partition("（")[0]
    if _normalized("".join(page.heading)) != _normalized(heading):
        raise FulltextError("正文页题名与目录不一致。")
    poems = [[]]
    for classes, text in page.rows:
        if not text:
            continue
        if "center-content" in classes and text in ("其二", "其三"):
            poems.append([])
        if "content" in classes:
            if text.startswith(("作者原注", "注释", "这首", "这两首", "这三首")):
                break
            poems[-1].append(text)
    else:
        raise FulltextError("未识别到诗文结束位置。")
    expected = {"十六字令三首": 3, "七律二首·送瘟神": 2, "七绝二首·纪念鲁迅八十寿辰": 2}.get(heading, 1)
    if len(poems) != expected or not all(poems):
        raise FulltextError("诗文篇数与书目不一致。")
    verses = ["".join(stanzas) for stanzas in poems]
    incipit = re.search(r"首句“([^”]+)”", title)
    if incipit and not verses[0].startswith(incipit.group(1)):
        raise FulltextError("同名作品的首句与目录不一致。")
    return verses


def _source_allowed(url):
    return ARTICLE_URL.fullmatch(url) or POEM_URL.fullmatch(url) or url == DABODI_URL


def _fetch(url):
    if not _source_allowed(url):
        raise FulltextError(f"无效的篇目来源：{url}")
    request = Request(url, headers={"User-Agent": "mao-wisdom/fulltext"})
    for attempt in range(2):
        try:
            with urlopen(request, timeout=20) as response:
                if not _source_allowed(response.geturl()):
                    raise FulltextError("下载地址已重定向到篇目目录以外。")
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise FulltextError("网页超出单篇大小限制。")
                length = response.headers.get("Content-Length")
                if length and int(length) != len(data):
                    raise FulltextError("网页下载不完整。")
                break
        except HTTPError as exc:
            if attempt or exc.code not in (408, 429, 500, 502, 503, 504):
                raise
        except (TimeoutError, URLError):
            if attempt:
                raise
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        # The site's older GB2312-labelled pages contain additional GBK characters.
        return data.decode("gb18030")


def _fold(char):
    if char in ("■", "�"):
        return char
    return "".join(c for c in unicodedata.normalize("NFKC", char).casefold() if c.isalnum())


def _normalized(text):
    return "".join(_fold(c) for c in text)


def _check_identity(db, application_id):
    if (db.execute("PRAGMA application_id").fetchone()[0] != application_id or
            db.execute("PRAGMA user_version").fetchone()[0] != VERSION):
        raise FulltextError("该文件与所查书目的全文索引不匹配，请核对 --collection 和索引路径。")


def _check_index(db, application_id):
    _check_identity(db, application_id)
    count = db.execute("SELECT work_count FROM build_info").fetchone()
    if not count or not count[0] or count[0] != db.execute("SELECT count(*) FROM works").fetchone()[0]:
        raise FulltextError("全文索引不完整，请重新构建。")
    empty = db.execute("""
        SELECT 1 FROM works w WHERE NOT EXISTS
        (SELECT 1 FROM paragraphs p WHERE p.work = w.id) LIMIT 1
    """).fetchone()
    if empty:
        raise FulltextError("全文索引缺少正文，请重新构建。")


def _read_index(path):
    return sqlite3.connect(path.absolute().as_uri() + "?mode=ro", uri=True)


def _check_target(path, application_id):
    if path.is_symlink():
        raise FulltextError("请指定普通索引文件，勿使用符号链接。")
    if path.exists():
        try:
            with closing(_read_index(path)) as db:
                _check_identity(db, application_id)
        except sqlite3.Error as exc:
            raise FulltextError("目标不是本工具可识别的索引，已保留原文件。") from exc


def build_index(path, works, *, fetch=None, poetry=False):
    path = Path(path)
    works = list(works)
    if not works or len({url for _, _, url in works}) != len(works):
        raise FulltextError("未找到篇目或篇目链接重复。")
    application_id = POETRY_ID if poetry else APPLICATION_ID
    _check_target(path, application_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    fetch = _fetch if fetch is None else fetch

    def load(work):
        volume, title, url = work
        try:
            html = fetch(url)
            return parse_poems(html, title, url) if poetry else parse_paragraphs(html)
        except (OSError, HTTPException, ValueError) as exc:
            raise FulltextError(f"{volume}《{title}》下载或解析失败：{exc}") from exc

    # Keep the staging database on the same filesystem so replacement is atomic.
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".mao-wisdom-", delete=False) as temp:
        staged = Path(temp.name)
    try:
        with closing(sqlite3.connect(staged)) as db:
            db.executescript(f"""
                PRAGMA application_id={application_id};
                PRAGMA user_version={VERSION};
                CREATE TABLE works (id INTEGER PRIMARY KEY, volume TEXT, title TEXT, url TEXT UNIQUE);
                CREATE TABLE paragraphs (work INTEGER, number INTEGER, text TEXT, folded TEXT,
                                         PRIMARY KEY (work, number));
                CREATE TABLE build_info (work_count INTEGER);
            """)
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = [pool.submit(load, work) for work in works]
                try:
                    for i, (work, future) in enumerate(zip(works, futures), 1):
                        paragraphs = future.result()
                        db.execute("INSERT INTO works VALUES (?,?,?,?)", (i, *work))
                        for n, paragraph in enumerate(paragraphs, 1):
                            key = paragraph
                            if poetry and work[1] == POEM_WITH_GAP:
                                # Preserve the displayed transcription and its character offsets.
                                key = key.replace("东瀛■剑有书还", "东瀛濯剑有书还")
                            db.execute("INSERT INTO paragraphs VALUES (?,?,?,?)",
                                       (i, n, paragraph, _normalized(key)))
                finally:
                    for future in futures:
                        future.cancel()
            db.execute("INSERT INTO build_info VALUES (?)", (len(works),))
            db.commit()
        _check_target(path, application_id)
        os.replace(staged, path)
    except sqlite3.Error as exc:
        raise FulltextError(f"无法写入全文索引：{exc}") from exc
    finally:
        staged.unlink(missing_ok=True)
    return len(works)


def _snippet(text, start, length):
    # SQLite positions are in normalized characters. Map them back to original
    # offsets so the excerpt retains the source's punctuation and full-width text.
    offsets = [i for i, char in enumerate(text) for _ in _fold(char)]
    left = max(0, offsets[start] - 30)
    right = min(len(text), offsets[start + length - 1] + 41, offsets[start] + 150)
    return ("…" if left else "") + text[left:right] + ("…" if right < len(text) else "")


def search_index(path, phrase, *, poetry=False):
    path = Path(path)
    term = _normalized(phrase)
    if not any(char.isalnum() for char in term):
        raise FulltextError("请输入包含文字或数字的检索词。")
    if not path.is_file():
        raise FulltextError("全文索引不存在，请先用 --build-index 构建。")
    try:
        with closing(_read_index(path)) as db:
            _check_index(db, POETRY_ID if poetry else APPLICATION_ID)
            rows = db.execute("""
                SELECT w.volume, w.title, w.url, p.number, p.text, instr(p.folded, ?)
                FROM paragraphs p JOIN works w ON w.id = p.work
                WHERE instr(p.folded, ?) > 0 ORDER BY p.work, p.number
            """, (term, term))
            for volume, title, url, n, text, position in rows:
                yield volume, title, url, n, _snippet(text, position - 1, len(term))
    except sqlite3.Error as exc:
        raise FulltextError(f"无法读取全文索引：{exc}") from exc
