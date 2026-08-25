"""Evidence package: run-directory creation, no-overwrite rule, manifests."""

import hashlib
import json
import os
import shutil
import tempfile
import unittest

from cvi_lab.evidence import EvidenceError, RunDirectory


class TestRunDirectory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cvi_evidence_test_")
        self.runs = os.path.join(self.tmp, "runs")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_structure(self):
        rd = RunDirectory(self.runs, "CVI-0_test")
        for sub in ("tasks", "prompts", "transcripts", "submissions",
                    "environment_logs"):
            self.assertTrue(os.path.isdir(os.path.join(rd.root, sub)))

    def test_never_overwrite_run(self):
        RunDirectory(self.runs, "CVI-0_test")
        with self.assertRaises(EvidenceError):
            RunDirectory(self.runs, "CVI-0_test")

    def test_never_overwrite_artifact(self):
        rd = RunDirectory(self.runs, "CVI-0_test")
        rd.write_text("tasks/a.json", "{}")
        with self.assertRaises(EvidenceError):
            rd.write_text("tasks/a.json", "{}")

    def test_manifest_and_hashes(self):
        rd = RunDirectory(self.runs, "CVI-0_test")
        rd.write_text("tasks/t.json", "hello")
        rd.write_json("scores.json", {"x": 1})
        rd.save_env_log("C", "A-01", 0, {"ok": True})
        manifest_path = rd.finalize()
        manifest = json.load(open(manifest_path))
        paths = {f["path"] for f in manifest["files"]}
        self.assertIn("tasks/t.json", paths)
        self.assertIn("scores.json", paths)
        # a file cannot list itself: the two special files are excluded
        self.assertNotIn("manifest.json", paths)
        self.assertNotIn("sha256_manifest.txt", paths)
        for f in manifest["files"]:
            with open(os.path.join(rd.root, f["path"]), "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            self.assertEqual(f["sha256"], digest,
                             f"bad hash for {f['path']}")
        sha_path = os.path.join(rd.root, "sha256_manifest.txt")
        self.assertTrue(os.path.isfile(sha_path))
        content = open(sha_path).read()
        self.assertIn("manifest.json sha256:", content)
        # the sha file covers manifest.json itself, with the right hash
        manifest_hash = hashlib.sha256(
            open(manifest_path, "rb").read()).hexdigest()
        self.assertIn(f"{manifest_hash}  manifest.json", content)
        for f in manifest["files"]:
            self.assertIn(f"{f['sha256']}  {f['path']}", content)


class TestArmRunIntoRealEvidenceSink(unittest.TestCase):
    """Regression: a full mock arm run (multiple phases submitting the
    same task) must never collide in the real evidence sink."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cvi_arm_test_")
        self.runs = os.path.join(self.tmp, "runs")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_full_arm_run_no_collisions(self):
        from cvi_lab import arms, generator
        from cvi_lab.config import PilotConfig
        from cvi_lab.participant import LLMResponse
        from cvi_lab.protocol import PilotProtocol

        tasks_a = generator.generate_family_a(4, 111111)
        tasks_b = generator.generate_family_b(tasks_a, 222222)
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        tasks_c = protocol.generate_family_c(seed=333333, tier=2)

        class Client:
            def __init__(self):
                self.progs = {}
                for t in tasks_a + tasks_b + tasks_c:
                    self.progs[t.task_id] = t.naive_program

            def complete(self, system, messages, max_tokens, label):
                return LLMResponse(
                    text="\n".join(
                        f"### TASK {tid}\n{p}\n### END\n"
                        for tid, p in self.progs.items()),
                    model="mock", stop_reason="end_turn",
                    input_tokens=1, output_tokens=1,
                    cache_read_tokens=0, cache_creation_tokens=0,
                    latency_s=0.0)

        rd = RunDirectory(self.runs, "CVI-0_test_arm")
        result = arms.run_arm_s(Client(), PilotConfig(), rd, tasks_a,
                                tasks_b, tasks_c)
        subs = os.listdir(os.path.join(rd.root, "submissions", "S", "A-01"))
        self.assertEqual(sorted(subs), ["v001.om", "v002.om"])
        rd.finalize({"status": "test"})


if __name__ == "__main__":
    unittest.main()
