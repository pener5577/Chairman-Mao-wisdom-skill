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
        self.assertEqual(re.findall(r"^(.+?)  \[已核原文\]", result.stdout, re.M), expected)

    def test_partial_phrase_and_work_title(self):
        result = search("前途是光明的道路是曲折的", "重庆谈判", "--verified")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("总之，前途是光明的，道路是曲折的。", result.stdout)
        self.assertEqual(result.stdout.count("[已核原文]"), 1)

    def test_unverified_wording_stays_a_lead(self):
        result = search("往往在于再坚持一下")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[待核线索]", result.stdout)
        self.assertNotIn("出处：", result.stdout)
        verified = search("--verified", "往往在于再坚持一下")
        self.assertEqual(verified.returncode, 1)
        self.assertFalse(verified.stdout)

    def test_no_match_and_invalid_query_have_different_exit_codes(self):
        self.assertEqual(search("青蛙乘坐无人地铁").returncode, 1)
        self.assertEqual(search("……").returncode, 2)
        self.assertEqual(search().returncode, 2)


if __name__ == "__main__":
    unittest.main()
