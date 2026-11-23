import os
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "scripts" / "search_quotes.py"
LIBRARY = PROJECT / "references" / "mao-quotes.md"


def search(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=tempfile.gettempdir(),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        encoding="utf-8",
    )


class QuoteSearchTests(unittest.TestCase):
    def test_verified_catalog_matches_library(self):
        catalog = LIBRARY.read_text(encoding="utf-8")
        blocks = re.split(r"^### ", catalog, flags=re.MULTILINE)[1:]
        expected = []
        for block in blocks:
            if "[核对原文](" in block:
                self.assertRegex(block, r"(?m)^> \S")
                expected.append(block.splitlines()[0])
        self.assertTrue(expected)
        result = search("--verified")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(re.findall(r"^(.+?)  \[检索标题\]", result.stdout, re.M), expected)
        self.assertEqual(result.stdout.count("[已核原文] "), len(expected))

    def test_partial_phrase_and_work_title(self):
        result = search("前途是光明的道路是曲折的", "重庆谈判", "--verified")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("总之，前途是光明的，道路是曲折的。", result.stdout)
        self.assertEqual(result.stdout.count("[已核原文]"), 1)
        self.assertIn("第1163页", result.stdout)
        self.assertIn("纸本页码：https://", result.stdout)

    def test_alias_and_source_can_match_one_entry(self):
        result = search("--verified", "吃梨子", "实践论")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("你要知道梨子的滋味", result.stdout)
        self.assertEqual(result.stdout.count("[已核原文]"), 1)
        self.assertFalse(search("--verified", "吃梨子", "重庆谈判").stdout)

    def test_work_title_precedes_broad_thematic_hits(self):
        result = search("--verified", "矛盾论")
        self.assertEqual(result.returncode, 0, result.stderr)
        blocks = result.stdout.strip().split("\n\n")
        self.assertIn("出处：《矛盾论》", blocks[0])
        self.assertTrue(any("出处：《实践论》" in block for block in blocks[1:]))

    def test_editorial_heading_is_not_labelled_as_a_verbatim_quote(self):
        result = search("--verified", "实践是检验真理的唯一标准")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[已核原文] 真理的标准只能是社会的实践。", result.stdout)
        self.assertNotIn("[已核原文] 实践是检验真理的唯一标准", result.stdout)
        self.assertIn("1978", result.stdout)
        self.assertIn("光明日报", result.stdout)

    def test_unverified_wording_stays_a_lead(self):
        result = search("往往在于再坚持一下")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[待核线索]", result.stdout)
        self.assertNotIn("出处：", result.stdout)
        verified = search("--verified", "往往在于再坚持一下")
        self.assertEqual(verified.returncode, 1)
        self.assertFalse(verified.stdout)

    def test_alternative_in_note_does_not_verify_the_heading(self):
        result = search("中国人死都不怕")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[待核线索]", result.stdout)
        self.assertIn("《别了，司徒雷登》", result.stdout)
        self.assertNotIn("[已核原文]", result.stdout)
        self.assertEqual(search("--verified", "中国人死都不怕").returncode, 1)

    def test_no_match_and_invalid_query_have_different_exit_codes(self):
        self.assertEqual(search("青蛙乘坐无人地铁").returncode, 1)
        self.assertEqual(search("……").returncode, 2)
        self.assertEqual(search().returncode, 2)

    def test_works_index_contains_all_five_volume_lists(self):
        result = search("--works")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = re.findall(r"^\[篇目\] (第.卷) · (.+)\n(https?://\S+)$", result.stdout, re.M)
        self.assertEqual(Counter(vol for vol, _, _ in rows), {
            "第一卷": 18, "第二卷": 40, "第三卷": 31, "第四卷": 70, "第五卷": 70,
        })
        self.assertEqual(len({(vol, title) for vol, title, _ in rows}), len(rows))
        self.assertIn("[附录] 第三卷附录 · 关于若干历史问题的决议", result.stdout)

    def test_collective_appendix_is_searchable_under_its_own_label(self):
        result = search("--works", "第3卷", "关于若干历史问题的决议")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[附录]", result.stdout)
        self.assertNotIn("[篇目]", result.stdout)

    def test_title_lookup_when_there_is_no_local_quote(self):
        result = search("为人民服务")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[篇目] 第三卷 · 为人民服务", result.stdout)
        self.assertNotIn("[已核原文]", result.stdout)
        self.assertEqual(search("--verified", "为人民服务").returncode, 1)

    def test_title_and_volume_must_both_match(self):
        result = search("--works", "第五卷", "《论十大关系》")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("[篇目]"), 1)
        self.assertIn("第五卷 · 论十大关系", result.stdout)
        self.assertEqual(search("--works", "第５卷", "论十大关系").stdout, result.stdout)
        self.assertEqual(search("--works", "第一卷", "论十大关系").returncode, 1)
        self.assertEqual(search("--works", "--verified").returncode, 2)

    def test_collected_works_lookup_and_volume_counts(self):
        listing = search("--collection", "文集")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        volumes = re.findall(r"^\[篇目\] 《毛泽东文集》(第.卷)", listing.stdout, re.M)
        self.assertEqual(Counter(volumes), {
            "第一卷": 67, "第二卷": 111, "第三卷": 77, "第四卷": 133,
            "第五卷": 116, "第六卷": 137, "第七卷": 72, "第八卷": 90,
        })
        result = search("--collection", "文集", "第１卷", "寻乌调查")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("《毛泽东文集》第一卷 · 寻乌调查", result.stdout)
        self.assertIn("核对目录：https://", result.stdout)
        self.assertEqual(search("寻乌调查").stdout, result.stdout)
        same_title = search("--collection", "文集", "第一卷", "给傅作义的信")
        self.assertEqual(same_title.stdout.count("[篇目]"), 2)
        self.assertIn("目录第 43 项", same_title.stdout)
        self.assertIn("目录第 53 项", same_title.stdout)
        self.assertIn("本卷电子版：https://", same_title.stdout)
        self.assertIn("正文：https://www.ssmzd.com/", search("--collection", "文集", "复李济深").stdout)
        self.assertEqual(search("--collection", "文集", "--text", "调查").returncode, 2)

    def test_poems_with_the_same_title_and_groups_of_poems(self):
        listing = search("--collection", "诗词")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        self.assertEqual(listing.stdout.count("《毛泽东诗词集》正编 · "), 39)
        self.assertEqual(listing.stdout.count("《毛泽东诗词集》副编 · "), 24)
        self.assertEqual(len(set(re.findall(r"^正文：(https://\S+)$", listing.stdout, re.M))), 63)
        result = search("--works", "--collection", "诗词", "浣溪沙", "和柳亚子")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("[篇目]"), 2)
        self.assertIn("1950年10月", result.stdout)
        self.assertIn("1950年11月", result.stdout)
        self.assertIn("十六字令三首", search("--collection", "诗词", "十六字令").stdout)


if __name__ == "__main__":
    unittest.main()
