import os
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")
BASH = shutil.which("bash")
if os.name == "nt" and GIT:
    git_bash = Path(GIT).resolve().parents[1] / "bin" / "bash.exe"
    BASH = str(git_bash) if git_bash.is_file() else None


@unittest.skipUnless(GIT and BASH, "本地同步验证需要 Git 和 Bash")
class SyncTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.work = root / "work"
        self.work.mkdir()
        self.origin = root / "origin.git"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0")
        self.git("init", "--bare", str(self.origin))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("remote", "add", "origin", str(self.origin))
        shutil.copyfile(PROJECT / "iteration.sh", self.work / "iteration.sh")
        (self.work / "SKILL.md").write_text("---\nname: mao-wisdom\n---\n", encoding="utf8")
        self.doc = self.work / "references" / "reading notes.md"
        self.doc.parent.mkdir()
        self.doc.write_text("original\n", encoding="utf8")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.git("push", "-u", "origin", "main")

    def git(self, *args, check=True):
        return subprocess.run([GIT, *args], cwd=self.work, env=self.env,
                              capture_output=True, check=check)

    def sync(self):
        return subprocess.run([BASH, "iteration.sh"], cwd=self.work, env=self.env,
                              capture_output=True, timeout=30)

    def remote_head(self):
        return self.git("--git-dir", str(self.origin), "rev-parse", "refs/heads/main").stdout

    def test_merge_conflict_stages_are_preserved(self):
        self.git("checkout", "-b", "topic")
        self.doc.write_text("topic\n", encoding="utf8")
        self.git("commit", "-am", "topic")
        self.git("checkout", "main")
        self.doc.write_text("main\n", encoding="utf8")
        self.git("commit", "-am", "main")
        self.assertNotEqual(self.git("merge", "topic", check=False).returncode, 0)
        conflicts = self.git("ls-files", "--unmerged").stdout
        self.assertEqual(len(conflicts.splitlines()), 3)
        original_head = self.remote_head()
        self.assertNotEqual(self.sync().returncode, 0)
        self.assertEqual(self.git("ls-files", "--unmerged").stdout, conflicts)
        self.assertEqual(self.remote_head(), original_head)

    def test_disguised_sqlite_is_refused_before_staging(self):
        cache = self.doc.parent / "cache.md"
        with closing(sqlite3.connect(cache)) as db:
            db.execute("CREATE TABLE cache (value TEXT)")
        self.doc.write_text("updated\n", encoding="utf8")
        original_head = self.remote_head()
        self.assertNotEqual(self.sync().returncode, 0)
        self.assertFalse(self.git("diff", "--cached", "--name-only").stdout)
        self.assertEqual(self.remote_head(), original_head)

    def test_removed_document_is_synced_to_remote(self):
        original_head = self.remote_head()
        self.doc.unlink()
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.remote_head(), original_head)
        listing = self.git("--git-dir", str(self.origin), "ls-tree", "-r", "--name-only", "main")
        self.assertNotIn(b"references/reading notes.md", listing.stdout)
