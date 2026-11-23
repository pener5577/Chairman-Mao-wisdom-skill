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
from fulltext import FulltextError, build_index, search_index


URL = "https://www.marxists.org/chinese/maozedong/sample.htm"
WORKS = [("第三卷", "样本篇目", URL)]
PAGE = """<html><head><title>样本篇目</title></head><body>
<a href="../index.html">站点导航</a><hr>
<p class="title1">样本篇目</p><p class="date">（一九四四年）</p>
<blockquote>＊ 这是编者给读者的说明。</blockquote>
　　读一页书，看一个例子。<br>
　　再把设想<a name="_ftnref1" href="#_ftn1">[1]</a>带回〔注：校注示例。——中文马克思主义文库〕实践。<br>
<hr width="60%"><span><a name="_ftn1">[1]</a>这个词的注释。</span>
</body></html>"""


class FulltextTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.index = Path(self.scratch.name) / "cache.sqlite3"

    def build(self):
        self.assertEqual(build_index(self.index, WORKS, fetch=lambda url: PAGE), 1)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(PROJECT / "scripts" / "search_quotes.py"),
             "--index-path", str(self.index), *args],
            cwd=self.scratch.name,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            encoding="utf-8", capture_output=True,
        )

    def test_cli_locates_original_passage_offline(self):
        self.build()
        result = self.cli("--text", "读一页书看一个例子")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[全文命中] 第三卷 · 样本篇目", result.stdout)
        self.assertIn("读一页书，看一个例子。", result.stdout)
        self.assertIn(URL, result.stdout)
        self.assertNotIn("[已核原文]", result.stdout)
        self.assertTrue(list(search_index(self.index, "设想带回实践")))

    def test_notes_navigation_and_paragraph_joins_do_not_match(self):
        self.build()
        for query in ("站点导航", "编者给读者", "这个词的注释", "校注示例", "例子再把"):
            with self.subTest(query=query):
                self.assertEqual(list(search_index(self.index, query)), [])

    def test_no_hit_missing_index_and_bad_arguments(self):
        self.assertEqual(self.cli("--text", "读一页书").returncode, 2)
        self.assertFalse(self.index.exists())
        self.build()
        self.assertEqual(self.cli("--text", "绝无此句").returncode, 1)
        self.assertEqual(self.cli("--text", "……").returncode, 2)
        self.assertEqual(self.cli("--text", "例子", "多余参数").returncode, 2)

    def test_limit_only_reports_truncation_when_other_paragraphs_matched(self):
        self.build()
        limited = self.cli("--text", "一", "--limit", "1")
        self.assertEqual(limited.returncode, 0, limited.stderr)
        self.assertFalse(limited.stderr)
        longer_page = PAGE.replace("再把设想", "再读一页，设想")
        build_index(self.index, WORKS, fetch=lambda url: longer_page)
        limited = self.cli("--text", "一", "--limit", "1")
        self.assertEqual(limited.stdout.count("[全文命中]"), 1)
        self.assertIn("前 1 个命中段落", limited.stderr)
        self.assertEqual(self.cli("--text", "一", "--limit", "0").returncode, 2)

    def test_an_incomplete_refresh_preserves_the_previous_index(self):
        self.build()

        def fetch(url):
            if url != URL:
                raise OSError("source unavailable")
            return PAGE.replace("读一页书", "读两页书")

        with self.assertRaises((FulltextError, OSError)):
            build_index(self.index, WORKS + [("第三卷", "另一样本", URL + "2")], fetch=fetch)
        self.assertTrue(list(search_index(self.index, "读一页书")))
        self.assertFalse(list(search_index(self.index, "读两页书")))

    def test_unrelated_database_is_never_replaced(self):
        with closing(sqlite3.connect(self.index)) as db:
            db.execute("CREATE TABLE personal_data (note TEXT)")
            db.execute("INSERT INTO personal_data VALUES ('keep')")
            db.commit()
        with self.assertRaises((FulltextError, OSError)):
            build_index(self.index, WORKS, fetch=lambda url: PAGE)
        with closing(sqlite3.connect(self.index)) as db:
            self.assertEqual(db.execute("SELECT note FROM personal_data").fetchone(), ("keep",))

    def test_rebuild_repairs_an_identifiable_incomplete_index(self):
        self.build()
        with closing(sqlite3.connect(self.index)) as db:
            db.execute("DELETE FROM paragraphs")
            db.commit()
        broken = self.cli("--text", "读一页书")
        self.assertEqual(broken.returncode, 2)
        self.assertIn("重新构建", broken.stderr)
        self.build()
        self.assertEqual(self.cli("--text", "读一页书").returncode, 0)


if __name__ == "__main__":
    unittest.main()
