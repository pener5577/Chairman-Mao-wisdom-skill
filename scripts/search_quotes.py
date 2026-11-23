"""检索毛泽东著作的摘句、篇目和本地全文索引。"""

import argparse
import re
import sys
import unicodedata
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


LIBRARY = Path(__file__).resolve().parents[1] / "references" / "mao-quotes.md"
WORKS = LIBRARY.with_name("works-index.md")
COLLECTIONS = {
    "选集": WORKS,
    "文集": LIBRARY.with_name("collected-works-index.md"),
    "诗词": LIBRARY.with_name("poetry-index.md"),
}
BOOK_NAMES = {"选集": "毛泽东选集", "文集": "毛泽东文集", "诗词": "毛泽东诗词集"}
VOLUME_NUMBERS = str.maketrans("一二三四五六七八", "12345678")
SOURCE_LINK = re.compile(r"\[核对原文\]\((https?://[^)\s]+)\)")
PAGE_LINK = re.compile(r"^\[查看纸本页码\]\((https?://[^)\s]+)\)$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


@dataclass
class Entry:
    theme: str
    heading: str
    excerpt: str
    citation: str
    url: Optional[str]
    aliases: tuple[str, ...]
    note: str
    page_url: Optional[str]


def field(lines, name):
    prefix = f"**{name}**"
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].lstrip(" ：:")
    return ""


def entries(markdown):
    for section in re.split(r"^## ", markdown, flags=re.MULTILINE)[1:]:
        theme, _, content = section.partition("\n")
        for block in re.split(r"^### ", content, flags=re.MULTILINE)[1:]:
            heading, _, body = block.partition("\n")
            lines = body.splitlines()
            excerpt = "\n".join(line[2:] for line in lines if line.startswith("> "))
            source = field(lines, "出处")
            link = SOURCE_LINK.search(source)
            page = PAGE_LINK.search(body)
            aliases = tuple(filter(None, re.split(r"[、\s]+", field(lines, "检索词"))))
            yield Entry(
                theme=theme, heading=heading, excerpt=excerpt,
                citation=SOURCE_LINK.sub("", source).strip(),
                url=link.group(1) if link and excerpt else None,
                aliases=aliases, note=field(lines, "辨析"),
                page_url=page.group(1) if page else None,
            )


def searchable(text):
    visible = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return "".join(c for c in unicodedata.normalize("NFKC", visible).casefold() if c.isalnum())


def match_rank(entry, terms):
    title = re.sub(r"^\d+\.\s*", "", entry.heading)
    # 按最弱的一项命中排序，多词分布在不同字段也可以找到。
    fields = [
        [searchable(entry.excerpt), searchable(title)],
        [searchable(alias) for alias in entry.aliases],
        [searchable(entry.citation)],
        [searchable(entry.note)],
        [searchable(entry.theme), searchable(entry.heading)],
    ]
    ranks = []
    for term in terms:
        for rank, values in enumerate(fields):
            if any(term in value for value in values):
                ranks.append(rank)
                break
        else:
            return None
    return max(ranks, default=0), sum(ranks)


def read_text(path, parser):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"无法读取 {path}：{error}\n")


def catalog_entries(catalog):
    volume = ""
    for line in catalog.splitlines():
        if line.startswith("## "):
            volume = line[3:] if re.fullmatch(r"## 第[一二三四五]卷(?:附录)?", line) else ""
            continue
        row = re.fullmatch(r"(?:\d+\.|-) \[([^\]]+)\]\((https?://[^\s)]+)\)", line)
        if volume and row:
            title, url = row.groups()
            yield volume, title, url


def bibliography_entries(markdown):
    section = ""
    sources = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            section, sources = line[3:].strip(), []
        if "[核对目录](" in line:
            sources = MARKDOWN_LINK.findall(line)
        row = re.fullmatch(r"(\d+)\. (.+)", line)
        if section and sources and row:
            number, title = row.groups()
            direct = MARKDOWN_LINK.fullmatch(title)
            links = sources
            if direct:
                title, url = direct.groups()
                links = [("正文", url), *sources]
            addresses = "\n".join(f"{label}：{url}" for label, url in links)
            yield section, title, f"目录第 {number} 项\n{addresses}"


def show_works(terms, parser, collections, *, after_quote_search=False):
    matches = []
    for collection in collections:
        markdown = read_text(COLLECTIONS[collection], parser)
        selected = collection == "选集"
        book = BOOK_NAMES[collection]
        rows = catalog_entries(markdown) if selected else bibliography_entries(markdown)
        for section, title, address in rows:
            numeric = section.translate(VOLUME_NUMBERS)
            fields = (searchable(title), book + section, book + numeric)
            if all(any(term in field for field in fields) for term in terms):
                kind = "附录" if section.endswith("附录") else "篇目"
                label = section if selected else f"《{book}》{section}"
                matches.append(f"[{kind}] {label} · {title}\n{address}")
    if matches:
        print("\n\n".join(matches))
        return 0
    if after_quote_search:
        print('语录和篇名均未命中。若记得一句原文，可用 --text "片段" 查已建立的全文索引。', file=sys.stderr)
    else:
        print("篇目目录未命中。可缩短篇名，或只输入卷次、正编或副编。", file=sys.stderr)
    return 1


def fulltext_command(args, parser):
    if __package__:
        from . import fulltext
    else:
        import fulltext

    path = (args.index_path or fulltext.DEFAULT_INDEX).expanduser()
    if args.keywords:
        parser.error("全文查找请把一个连续片段放在 --text 后；建库命令无需关键词")
    try:
        if args.build_index:
            catalog = [row for row in catalog_entries(read_text(WORKS, parser)) if not row[0].endswith("附录")]
            counts = Counter(volume for volume, _, _ in catalog)
            if counts != {"第一卷": 18, "第二卷": 40, "第三卷": 31, "第四卷": 70, "第五卷": 70}:
                parser.exit(2, "篇目目录不完整，未开始建库。\n")
            print(f"正在从目录中的 {len(catalog)} 篇在线转录建立索引……", file=sys.stderr, flush=True)
            count = fulltext.build_index(path, catalog)
            print(f"已索引 {count} 篇作品。索引文件：{path}")
            return 0
        limit = args.limit or 20
        shown = 0
        with closing(fulltext.search_index(path, args.text)) as matches:
            for volume, title, url, number, snippet in matches:
                if shown == limit:
                    print(f"已显示前 {limit} 个命中段落。可输入更长的片段缩小范围，或调大 --limit。", file=sys.stderr)
                    break
                if shown:
                    print()
                print(f"[全文命中] {volume} · {title}（转录段 {number}）\n{snippet}\n{url}")
                shown += 1
        if shown:
            return 0
        print("本地全文索引中未找到该片段。可以缩短引文，或换一种用字再查。", file=sys.stderr)
        return 1
    except (fulltext.FulltextError, OSError) as error:
        parser.exit(2, f"{error}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keywords", nargs="*", help="主题、篇名或正文中的关键词，多个词须同时命中")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verified", action="store_true", help="只列出附有核对原文链接的摘句")
    mode.add_argument("--works", action="store_true", help="查《毛泽东选集》一至五卷的篇名或卷次，无关键词时列出全部篇目")
    mode.add_argument("--build-index", action="store_true", help="联网建立或更新一至五卷的本地全文索引")
    mode.add_argument("--text", metavar="引文", help="从已建索引离线定位一段连续文字")
    parser.add_argument("--collection", choices=COLLECTIONS, help="按书查目录，可选选集、文集、诗词")
    parser.add_argument("--index-path", type=Path, metavar="文件", help="指定建库或全文查找使用的 SQLite 文件")
    parser.add_argument("--limit", type=int, metavar="条数", help="全文命中段落的显示上限，默认 20")
    args = parser.parse_args()
    if args.collection and (args.verified or args.build_index or args.text is not None):
        parser.error("--collection 用于篇目目录，可单独使用或与 --works 一起使用")
    if args.limit is not None and (args.text is None or args.limit < 1):
        parser.error("--limit 仅用于 --text，请输入正整数")
    if args.build_index or args.text is not None:
        return fulltext_command(args, parser)
    if args.index_path is not None:
        parser.error("--index-path 仅用于 --build-index 或 --text")
    terms = [searchable(word) for arg in args.keywords for word in arg.split()]
    if (not terms and not (args.verified or args.works or args.collection)) or any(not term for term in terms):
        parser.error("请输入文字关键词，或使用 --verified 浏览已核摘句、--works 浏览篇目")

    if args.works or args.collection:
        return show_works(terms, parser, (args.collection or "选集",))

    matches = []
    for entry in entries(read_text(LIBRARY, parser)):
        if args.verified and not entry.url:
            continue
        rank = match_rank(entry, terms)
        if rank is not None:
            matches.append((rank, entry))
    if not matches:
        if not args.verified:
            return show_works(terms, parser, COLLECTIONS, after_quote_search=True)
        print("已核摘句未命中。可缩短关键词，或去掉 --verified 查找线索和篇目。", file=sys.stderr)
        return 1
    for index, (_, entry) in enumerate(sorted(matches, key=lambda item: item[0])):
        if index:
            print()
        label = "检索标题" if entry.url else "待核线索"
        print(f"{entry.heading}  [{label}]  {entry.theme}")
        if entry.url:
            print(f"[已核原文] {entry.excerpt}\n出处：{entry.citation}\n{entry.url}")
            if entry.page_url:
                print(f"纸本页码：{entry.page_url}")
        elif entry.citation:
            print(f"查找线索：{entry.citation}")
        if entry.note:
            print(f"辨析：{entry.note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
