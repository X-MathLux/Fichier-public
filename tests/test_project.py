"""Behavior tests: disposable Git repositories, never the user's Git configuration."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("project_coordinator", Path(__file__).resolve().parents[1] / "scripts" / "project.py")
project = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project)


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        # Keep disposable repos inside this checkout: some Windows sandboxes give
        # Python and its Git child different access to the system temp directory.
        temporary_root = Path(project.__file__).resolve().parents[1] / ".local" / "test-tmp"
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="test-", dir=temporary_root)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Coordinator Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(".local/\ntasks/.board.lock\n", encoding="utf-8")
        (self.root / "README.md").write_text("Test fixture\n", encoding="utf-8")
        (self.root / "evidence.md").write_text("Commands and observed results\n", encoding="utf-8")
        (self.root / "review.md").write_text("Independent inspection\n", encoding="utf-8")
        self.cli("init", "--name", "fixture", "--goal", "Exercise coordinator")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args, cwd=None, expected=0):
        result = subprocess.run(["git", "-C", str(cwd or self.root), *args], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result.stdout

    def cli(self, *args, expected=0):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            result = project.main(["--root", str(self.root), *args])
        self.assertEqual(result, expected, error.getvalue() + output.getvalue())
        return json.loads(output.getvalue()) if output.getvalue() else error.getvalue()

    def state(self):
        return json.loads((self.root / "tasks" / "board.json").read_text(encoding="utf-8"))

    def write_state(self, data):
        (self.root / "tasks" / "board.json").write_text(json.dumps(data), encoding="utf-8")

    def add(self, role="implementer", path="src/", depends=()):
        args = ["task", "add", "--title", "Make a tested change", "--role", role, "--accept", "Observed result meets criterion"]
        if path is not None:
            args += ["--path", path]
        for dep in depends:
            args += ["--depends", dep]
        return self.cli(*args)["id"]

    def ready(self, tid):
        self.cli("task", "ready", tid)

    def start_read_only(self):
        tid = self.add(role="researcher", path=None)
        self.ready(tid)
        self.cli("task", "start", tid, "--worker", "research-worker")
        return tid

    def submitted_implementation(self):
        tid = self.add()
        self.ready(tid)
        record = self.cli("worktree", tid)
        wt = self.root / record["path"]
        self.cli("task", "start", tid, "--worker", "builder")
        (wt / "src").mkdir()
        (wt / "src" / "feature.txt").write_text("working feature\n", encoding="utf-8")
        self.git("add", "src/feature.txt", cwd=wt)
        self.git("commit", "-m", "feature", cwd=wt)
        sha = self.git("rev-parse", "HEAD", cwd=wt).strip()
        self.cli("task", "submit", tid, "--commit", sha, "--evidence", "evidence.md")
        return tid, wt, sha

    def test_dag_planning_is_deterministic_and_excludes_overlap(self):
        first = self.add(path="src/")
        overlapping = self.add(path="SRC/feature.py")
        independent = self.add(path="docs/")
        dependent = self.add(role="verifier", path=None, depends=[first])
        for tid in (first, overlapping, independent, dependent):
            self.ready(tid)
        result = self.cli("plan")
        self.assertEqual(result["wave"], [first, independent])
        self.assertEqual(result["skipped"][overlapping], "scope conflict")
        self.assertEqual(result["skipped"][dependent], "dependencies")
        self.cli("task", "start", dependent, "--worker", "premature", expected=2)

    def test_scope_ancestors_casefold_and_file_collisions(self):
        self.assertTrue(project.overlap("src", "SRC/nested.py"))
        self.assertTrue(project.overlap("src/", "src/nested.py"))
        self.assertTrue(project.overlap("src/feature.py", "SRC/FEATURE.PY"))
        self.assertFalse(project.overlap("src/", "src-other/a.py"))
        self.assertFalse(project.covers(["src"], "src/nested.py"))

    def test_invalid_paths_and_secret_references_are_rejected(self):
        for invalid in ("../escape/", "/absolute/", "C:/absolute/", ".git/", "src/../../bad", "src/*.py", "src\\bad", "src//bad", "src/./bad"):
            with self.subTest(path=invalid):
                self.cli("task", "add", "--title", "bad", "--role", "implementer", "--path", invalid, "--accept", "valid", expected=2)
        (self.root / ".env").write_text("PRIVATE=not-ingested", encoding="utf-8")
        self.cli("task", "add", "--title", "bad research", "--role", "researcher", "--accept", "criterion", "--research", ".env", expected=2)
        self.assertEqual(self.state()["tasks"], [])

    def test_symlink_escape_rejected(self):
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        link = self.root / "escape"
        try:
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("OS does not grant permission to create symlinks")
            with self.assertRaises(project.ProjectError):
                project.confined(self.root, "escape/file.txt")
        finally:
            if link.is_symlink():
                link.unlink()
            outside.rmdir()

    def test_lock_busy_does_not_remove_or_write_someone_elses_lock(self):
        before = (self.root / "tasks" / "board.json").read_bytes()
        lock = self.root / "tasks" / ".board.lock"
        lock.write_text("other-coordinator", encoding="utf-8")
        self.cli("task", "add", "--title", "busy", "--role", "researcher", "--accept", "criterion", expected=2)
        self.assertEqual(lock.read_text(encoding="utf-8"), "other-coordinator")
        self.assertEqual((self.root / "tasks" / "board.json").read_bytes(), before)

    def test_atomic_write_failure_preserves_old_board_and_releases_own_lock(self):
        before = (self.root / "tasks" / "board.json").read_bytes()
        with patch.object(project.os, "replace", side_effect=OSError("simulated disk error")):
            self.cli("task", "add", "--title", "atomic", "--role", "researcher", "--accept", "criterion", expected=2)
        self.assertEqual((self.root / "tasks" / "board.json").read_bytes(), before)
        self.assertFalse((self.root / "tasks" / ".board.lock").exists())
        self.assertEqual(list((self.root / "tasks").glob(".board-*.tmp")), [])

    def test_validation_rejects_bad_types_missing_dependencies_and_cycles(self):
        one = self.add(role="researcher", path=None)
        two = self.add(role="reviewer", path=None)
        original = self.state()
        for mutate in (
            lambda b: b["tasks"][0].update(role=[]),
            lambda b: b["tasks"][0].update(status={}),
            lambda b: b["tasks"][0].update(depends_on=["T9999"]),
            lambda b: (b["tasks"][0].update(depends_on=[two]), b["tasks"][1].update(depends_on=[one])),
        ):
            data = json.loads(json.dumps(original))
            mutate(data)
            self.write_state(data)
            self.cli("validate", expected=2)

    def test_same_worker_review_rejected_and_read_only_lifecycle(self):
        tid = self.start_read_only()
        self.cli("task", "submit", tid, "--commit", self.base, "--evidence", "evidence.md")
        self.cli("task", "review", tid, "--commit", self.base, "--reviewer", "RESEARCH-WORKER", "--decision", "pass", "--report", "review.md", expected=2)
        self.cli("task", "close", tid, "--integrated-commit", self.base, expected=2)
        self.cli("task", "review", tid, "--commit", self.base, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        self.cli("task", "close", tid, "--integrated-commit", self.base)
        task = self.state()["tasks"][0]
        self.assertEqual(task["status"], "done")
        self.assertEqual([h["event"] for h in task["history"]], ["created", "ready", "started", "submitted", "reviewed", "closed"])

    def test_failure_retries_are_bounded(self):
        tid = self.start_read_only()
        for attempt in (1, 2):
            self.cli("task", "submit", tid, "--commit", self.base, "--evidence", "evidence.md")
            self.cli("task", "review", tid, "--commit", self.base, "--reviewer", "independent", "--decision", "fail", "--report", "review.md")
            if attempt == 1:
                self.cli("task", "start", tid, "--worker", "research-worker")
        self.assertEqual(self.cli("plan")["skipped"][tid], "attempt limit")
        self.cli("task", "start", tid, "--worker", "research-worker", expected=2)

    def test_start_implementation_requires_worktree_and_reserves_scope(self):
        tid = self.add()
        self.ready(tid)
        self.cli("task", "start", tid, "--worker", "builder", expected=2)
        self.cli("worktree", tid)
        self.cli("task", "start", tid, "--worker", "builder")
        another = self.add(path="SRC/other.py")
        self.ready(another)
        self.cli("task", "start", another, "--worker", "other-builder", expected=2)
        self.assertEqual(self.cli("plan")["skipped"][another], "scope conflict")

    def test_submitted_tasks_reserve_scopes_but_release_agent_slots(self):
        cfg_path = self.root / "project.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["orchestration"]["max_parallel_agents"] = 1
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        self.git("add", "project.json")
        self.git("commit", "-m", "single agent slot")
        tid, wt, sha = self.submitted_implementation()
        other = self.add(path="docs/")
        collision = self.add(path="src/other.txt")
        self.ready(other)
        self.ready(collision)
        self.assertEqual(self.cli("plan")["wave"], [other])
        self.assertEqual(self.cli("plan")["skipped"][collision], "scope conflict")

    def test_only_integrator_can_request_engine_scope(self):
        self.add(path="scripts/application.py")
        self.cli("task", "add", "--title", "protected", "--role", "implementer", "--path", "scripts/project.py", "--accept", "criterion", expected=2)
        self.add(role="integrator", path="scripts/project.py")
        self.cli("task", "add", "--title", "board protected", "--role", "integrator", "--path", "tasks/board.json", "--accept", "criterion", expected=2)

    def test_worktree_isolation_pinned_base_and_no_overwrite(self):
        tid = self.add()
        record = self.cli("worktree", tid)
        wt = self.root / record["path"]
        self.assertEqual(record["base_commit"], self.base)
        self.assertEqual(self.git("branch", "--show-current", cwd=wt).strip(), "task/" + tid)
        (wt / "scratch.txt").write_text("isolated", encoding="utf-8")
        self.assertFalse((self.root / "scratch.txt").exists())
        self.cli("worktree", tid, expected=2)
        self.assertEqual((wt / "scratch.txt").read_text(encoding="utf-8"), "isolated")

    def test_task_worktree_cannot_mutate_its_own_copy_of_board(self):
        tid = self.add()
        record = self.cli("worktree", tid)
        wt = self.root / record["path"]
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            result = project.main(["--root", str(wt), "task", "add", "--title", "rogue board", "--role", "researcher", "--accept", "criterion"])
        self.assertEqual(result, 2)
        self.assertIn("Task worktrees cannot mutate", error.getvalue())
        self.assertEqual(len(self.state()["tasks"]), 1)

    def test_worktree_refuses_dirty_tracked_tree_and_preexisting_branch(self):
        tid = self.add()
        (self.root / "README.md").write_text("uncommitted change", encoding="utf-8")
        self.cli("worktree", tid, expected=2)
        self.git("restore", "README.md")
        self.git("branch", "task/" + tid)
        self.cli("worktree", tid, expected=2)
        self.assertFalse((self.root / ".local" / "worktrees" / tid).exists())

    def test_dependency_worktree_requires_done_provider_and_integrated_base(self):
        provider, provider_wt, provider_sha = self.submitted_implementation()
        consumer = self.add(path="consumer/", depends=[provider])
        self.ready(consumer)
        self.assertIn("Dependency must be done", self.cli("worktree", consumer, expected=2))
        self.cli("task", "review", provider, "--commit", provider_sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        self.git("merge", "--ff-only", provider_sha)
        self.cli("task", "close", provider, "--integrated-commit", provider_sha)
        self.assertIn("does not contain dependency integration", self.cli("worktree", consumer, "--base", self.base, expected=2))
        self.assertFalse((self.root / ".local" / "worktrees" / consumer).exists())
        record = self.cli("worktree", consumer)
        wt = self.root / record["path"]
        self.assertEqual((wt / "src" / "feature.txt").read_text(encoding="utf-8"), "working feature\n")
        self.cli("task", "start", consumer, "--worker", "consumer-builder")
        self.assertEqual(self.state()["tasks"][1]["status"], "running")

    def test_start_rejects_persisted_worktree_missing_dependency_integration(self):
        provider, provider_wt, provider_sha = self.submitted_implementation()
        consumer = self.add(path="consumer/", depends=[provider])
        self.ready(consumer)
        # Simulate a persisted worktree created under the earlier coordinator.
        relative = f".local/worktrees/{consumer}"
        wt = self.root / relative
        self.git("worktree", "add", "-b", f"task/{consumer}", str(wt), self.base)
        data = self.state()
        data["tasks"][1]["worktree"] = {"path": relative, "branch": f"task/{consumer}", "base_commit": self.base}
        self.write_state(data)
        self.cli("task", "review", provider, "--commit", provider_sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        self.git("merge", "--ff-only", provider_sha)
        self.cli("task", "close", provider, "--integrated-commit", provider_sha)
        failure = self.cli("task", "start", consumer, "--worker", "consumer-builder", expected=2)
        self.assertIn("does not contain dependency integration", failure)
        self.assertEqual(self.state()["tasks"][1]["status"], "ready")

    def test_submit_rejects_out_of_scope_changes(self):
        tid = self.add(path="src/")
        self.ready(tid)
        record = self.cli("worktree", tid)
        wt = self.root / record["path"]
        self.cli("task", "start", tid, "--worker", "builder")
        (wt / "README.md").write_text("out of scope", encoding="utf-8")
        self.git("add", "README.md", cwd=wt)
        self.git("commit", "-m", "invalid scope", cwd=wt)
        sha = self.git("rev-parse", "HEAD", cwd=wt).strip()
        self.cli("task", "submit", tid, "--commit", sha, "--evidence", "evidence.md", expected=2)
        self.assertEqual(self.state()["tasks"][0]["status"], "running")

    def test_close_requires_reviewed_content_in_head_and_supports_cherry_pick(self):
        tid, wt, sha = self.submitted_implementation()
        self.cli("task", "review", tid, "--commit", sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        self.cli("task", "close", tid, "--integrated-commit", sha, expected=2)
        self.cli("task", "close", tid, "--integrated-commit", self.base, expected=2)
        # An unrelated coordinator commit forces a different cherry-picked SHA.
        (self.root / "unrelated.txt").write_text("other task", encoding="utf-8")
        self.git("add", "unrelated.txt")
        self.git("commit", "-m", "unrelated")
        self.git("cherry-pick", sha)
        integrated = self.git("rev-parse", "HEAD").strip()
        self.assertNotEqual(integrated, sha)
        self.cli("task", "close", tid, "--integrated-commit", integrated)
        self.assertEqual(self.state()["tasks"][0]["status"], "done")

    def test_resubmission_invalidates_review_and_detects_stale_board_review(self):
        tid, wt, sha = self.submitted_implementation()
        self.cli("task", "review", tid, "--commit", sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        (wt / "src" / "feature.txt").write_text("revised feature\n", encoding="utf-8")
        self.git("add", "src/feature.txt", cwd=wt)
        self.git("commit", "-m", "revision", cwd=wt)
        revised = self.git("rev-parse", "HEAD", cwd=wt).strip()
        self.cli("task", "submit", tid, "--commit", revised, "--evidence", "evidence.md")
        task = self.state()["tasks"][0]
        self.assertIsNone(task["review"])
        self.assertEqual(task["status"], "submitted")
        # A report prepared before resubmission must not approve the new candidate.
        self.assertIn("stale report", self.cli("task", "review", tid, "--commit", sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md", expected=2))
        data = self.state()
        data["tasks"][0]["review"] = {"reviewer": "independent", "decision": "pass", "commit": sha, "report": "review.md"}
        self.write_state(data)
        self.assertIn("Stale review", self.cli("validate", expected=2))

    def test_close_rejects_head_drift_but_accepts_later_valid_checkpoint(self):
        tid, wt, sha = self.submitted_implementation()
        self.cli("task", "review", tid, "--commit", sha, "--reviewer", "independent", "--decision", "pass", "--report", "review.md")
        self.git("merge", "--ff-only", sha)
        feature = self.root / "src" / "feature.txt"
        feature.write_text("unreviewed later change\n", encoding="utf-8")
        self.git("add", "src/feature.txt")
        self.git("commit", "-m", "later unreviewed content")
        failure = self.cli("task", "close", tid, "--integrated-commit", sha, expected=2)
        self.assertIn("Current HEAD content differs", failure)
        self.assertEqual(self.state()["tasks"][0]["status"], "reviewed")
        # A later checkpoint is permitted when current HEAD retains reviewed content.
        feature.write_text("working feature\n", encoding="utf-8")
        self.git("add", "src/feature.txt", "tasks/board.json")
        self.git("commit", "-m", "restore reviewed content and checkpoint board")
        self.assertNotEqual(self.git("rev-parse", "HEAD").strip(), sha)
        self.cli("task", "close", tid, "--integrated-commit", sha)
        self.assertEqual(self.state()["tasks"][0]["status"], "done")

    def test_packet_uses_references_without_ingesting_research_body(self):
        (self.root / "research.md").write_text("UNTRUSTED PRIVATE BODY MUST NOT APPEAR", encoding="utf-8")
        tid = self.cli("task", "add", "--title", "Research", "--role", "researcher", "--accept", "criterion", "--research", "research.md")["id"]
        packet = self.cli("packet", tid)
        self.assertEqual(packet["task"]["research"], "research.md")
        self.assertNotIn("UNTRUSTED PRIVATE", json.dumps(packet))

    def test_missing_application_checks_fail(self):
        result = self.cli("check", "--application", expected=2)
        self.assertIn("No application checks configured", result)

    def test_application_checks_success_failure_timeout_and_argv(self):
        path = self.root / "project.json"
        cfg = json.loads(path.read_text(encoding="utf-8"))
        cfg["checks"]["application"] = [
            ["{python}", "-c", "print('actual pass')"],
            ["{python}", "-c", "raise SystemExit(7)"],
            ["{python}", "-c", "import time; time.sleep(5)"],
            ["{python}", "-c", "import sys; print(sys.argv[1])", "literal; $(no-shell)"],
        ]
        path.write_text(json.dumps(cfg), encoding="utf-8")
        result = self.cli("check", "--application", "--timeout", "1", expected=1)
        self.assertFalse(result["passed"])
        self.assertEqual([r["passed"] for r in result["results"]], [True, False, False, True])
        self.assertEqual(result["results"][1]["returncode"], 7)
        self.assertIn("Timeout", result["results"][2]["error"])
        self.assertIn("literal; $(no-shell)", result["results"][3]["stdout"])

    def test_cli_subprocess_entrypoint(self):
        result = subprocess.run([sys.executable, str(Path(project.__file__)), "--root", str(self.root), "doctor"], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
