import os
import re
import subprocess
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
