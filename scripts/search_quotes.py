"""在本地 Markdown 语录库中按关键词检索。"""

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


LIBRARY = Path(__file__).resolve().parents[1] / "references" / "mao-quotes.md"
SOURCE_LINK = re.compile(r"\[核对原文\]\((https?://[^)\s]+)\)")
PAGE_LINK = re.compile(r"^\[查看纸本页码\]\((https?://[^)\s]+)\)$", re.MULTILINE)


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keywords", nargs="*", help="主题、篇名或正文中的关键词，多个词须同时命中")
    parser.add_argument("--verified", action="store_true", help="只列出附有核对原文链接的条目")
    args = parser.parse_args()
    terms = [searchable(word) for arg in args.keywords for word in arg.split()]
    if (not terms and not args.verified) or any(not term for term in terms):
        parser.error("请输入文字关键词，或使用 --verified 浏览已核条目")

    try:
        markdown = LIBRARY.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"无法读取语录库 {LIBRARY}：{error}\n")

    matches = []
    for entry in entries(markdown):
        if args.verified and not entry.url:
            continue
        rank = match_rank(entry, terms)
        if rank is not None:
            matches.append((rank, entry))
    if not matches:
        print("没有匹配条目。可缩短关键词，或改用篇名、主题词。", file=sys.stderr)
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
