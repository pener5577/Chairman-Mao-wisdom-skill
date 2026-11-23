"""在本地 Markdown 语录库中按关键词检索。"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path


LIBRARY = Path(__file__).resolve().parents[1] / "references" / "mao-quotes.md"
SOURCE_LINK = re.compile(r"\[核对原文\]\((https?://[^)\s]+)\)")


def entries(markdown):
    for section in re.split(r"^## ", markdown, flags=re.MULTILINE)[1:]:
        theme, _, content = section.partition("\n")
        for block in re.split(r"^### ", content, flags=re.MULTILINE)[1:]:
            heading, _, body = block.partition("\n")
            lines = body.splitlines()
            excerpt = "\n".join(line[2:] for line in lines if line.startswith("> "))
            source = next((line for line in lines if line.startswith("**出处**")), "")
            link = SOURCE_LINK.search(source)
            citation = SOURCE_LINK.sub("", source).removeprefix("**出处**").strip(" ：:｜|")
            yield theme, heading, excerpt, citation, link.group(1) if link and excerpt else None


def searchable(text):
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


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

    found = False
    for theme, heading, excerpt, citation, url in entries(markdown):
        if args.verified and not url:
            continue
        fields = [searchable(value) for value in (theme, heading, excerpt, citation)]
        if not all(any(term in field for field in fields) for term in terms):
            continue
        if found:
            print()
        found = True
        status = "已核原文" if url else "待核线索"
        print(f"{heading}  [{status}]  {theme}")
        if url:
            print(excerpt)
            print(f"出处：{citation}\n{url}")
        elif citation:
            print(f"查找线索：{citation}")
    if not found:
        print("没有匹配条目。可缩短关键词，或改用篇名、主题词。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
