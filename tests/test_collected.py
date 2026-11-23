import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
from collected_index import build_index, search_index
from fulltext import FulltextError


PDF = "https://www.cdct.edu.cn/uploadfile/24/file/20230529/1685342597109442.pdf"
WORKS = [("第一卷", 1, "同题", PDF + "#page=2"), ("第一卷", 2, "同题", PDF + "#page=6")]


def parsed_sample(data, entries):
    assert [n for n, _, _ in entries] == [1, 2]
    yield 1, "正文", 2, 3, "我们观察两组\f不同现象。"
    yield 1, "编注", 4, 4, "这是编者整理材料时所写的一段话。"
    yield 2, "正文", 6, 6, "这里的正文只出现一次。"
    yield 2, "版面", 6, 6, "图表样本。"


class CollectedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "collected.sqlite3"

    def build(self):
        fetched = []

        def fetch(url):
            fetched.append(url)
            return b"%PDF-1.7\n"

        self.assertEqual(build_index(self.path, WORKS, fetch=fetch, parse=parsed_sample), 2)
        self.assertEqual(fetched, [PDF])

    def cli(self, *args):
        # -S excludes all installed third-party packages from the query process.
        return subprocess.run(
            [sys.executable, "-S", str(PROJECT / "scripts/search_quotes.py"),
             "--index-path", str(self.path), "--collection", "文集", *args],
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            cwd=self.temp.name, encoding="utf-8", capture_output=True,
        )

    def test_real_page_boundaries_and_no_crossing_into_another_work(self):
        self.build()
        for query, start, end in [("两组，不同", 2, 3), ("不同现象", 3, 3), ("正文只出现", 6, 6)]:
            with self.subTest(query=query):
                row, = search_index(self.path, query)
                self.assertEqual(row[:6], ("第一卷", "同题", f"{PDF}#page={start}", start, end, "正文"))
        self.assertFalse(list(search_index(self.path, "现象这是编者")))
        self.assertFalse(list(search_index(self.path, "一段话这里的正文")))

    def test_text_classes_and_search_without_the_pdf_dependency(self):
        self.build()
        result = self.cli("--text", "编者整理")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[编注命中]", result.stdout)
        self.assertIn("PDF 第 4 页", result.stdout)
        self.assertEqual(self.cli("--text", "编者整理", "--part", "正文").returncode, 1)
        self.assertIn("[版面命中]", self.cli("--text", "图表", "--part", "版面").stdout)
        self.assertEqual(self.cli("--text", "……").returncode, 2)

    def test_failed_refresh_preserves_old_index_and_rejects_other_databases(self):
        self.build()
        def broken(data, items):
            yield 1, "正文", 2, 2, "只下载了一部分。"
            raise OSError("读入中断")

        with self.assertRaises((FulltextError, OSError)):
            build_index(self.path, WORKS, fetch=lambda url: b"%PDF-1.7\n", parse=broken)
        self.assertTrue(list(search_index(self.path, "不同现象")))
        self.assertFalse(list(search_index(self.path, "一部分")))
        other = Path(self.temp.name) / "other.sqlite3"
        with closing(sqlite3.connect(other)) as db:
            db.execute("CREATE TABLE personal (id INTEGER)")
            db.commit()
        before = other.read_bytes()
        with self.assertRaises(FulltextError):
            build_index(other, WORKS, fetch=lambda url: b"%PDF-1.7\n", parse=parsed_sample)
        self.assertEqual(other.read_bytes(), before)

    def test_missing_pdf_reader_reports_setup_before_downloading(self):
        result = self.cli("--build-index")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("PyMuPDF", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.path.exists())


# These references use the PDF viewer's physical page numbers, including covers.
# Set the path to an existing eight-volume index to rerun the edition checks offline.
@unittest.skipUnless(os.environ.get("MAO_WISDOM_TEST_COLLECTED_INDEX"), "需要已建好的真实八卷索引")
class PublishedEditionTests(unittest.TestCase):
    def test_original_passages_notes_and_cross_page_links_in_all_volumes(self):
        path = os.environ["MAO_WISDOM_TEST_COLLECTED_INDEX"]
        examples = [
            ("沿途做了一点简略调查", "第一卷", "《东塘等处调查》前言", 257, 257, "正文"),
            ("工作才有做好的希望", "第二卷", "《文化课本》序言", 400, 400, "正文"),
            ("今天延安大学开学", "第三卷", "在延安大学开学典礼上的讲话", 160, 160, "正文"),
            ("关于戏，我是个外行，只会看", "第四卷", "改造旧艺术 创造新艺术", 338, 338, "正文"),
            ("从前我当小学教员时", "第五卷", "依靠群众办好铁路建设事业", 318, 318, "正文"),
            ("当地从事文学艺术工作的负责同志", "第六卷", "在文学艺术界开展整风学习", 202, 202, "正文"),
            ("逐章逐节加以讨论", "第七卷", "关于读书的建议", 441, 441, "正文"),
            ("要多得占篇幅五分之一左右", "第八卷", "《人民日报》要多登科学讨论文章", 97, 97, "正文"),
            ("这一点很要紧", "第一卷", "所希望于劳工会的", 17, 18, "正文"),
            ("通过讨论，打通思想", "第七卷", "同藏族人士的谈话", 13, 14, "正文"),
            ("当时在法国勤工俭学", "第一卷", "给蔡和森的信", 16, 16, "编注"),
            ("本篇二是毛泽东对电影", "第八卷", "党的文艺政策应当调整", 456, 456, "编注"),
            ("指一九五九年八月二十一日", "第八卷", "《人民日报》要多登科学讨论文章", 97, 97, "编注"),
        ]
        for phrase, volume, title, first, last, kind in examples:
            with self.subTest(phrase=phrase):
                actual = [(v, t, p, q, k) for v, t, url, p, q, k, _ in search_index(path, phrase)
                          if url.endswith(f"#page={p}")]
                self.assertIn((volume, title, first, last, kind), actual)
        for term in ("www.mzdbl.cn", "图书在版编目", "ISBN978-7-01-003029-6"):
            with self.subTest(term=term):
                self.assertFalse(list(search_index(path, term)))


if __name__ == "__main__":
    unittest.main()
