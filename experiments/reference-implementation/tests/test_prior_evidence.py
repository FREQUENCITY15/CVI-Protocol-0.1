"""Prior evidence immutability (CVI-0.1 requirement 16).

Every sealed run directory (any directory under runs/ that contains a
sha256_manifest.txt — including all CVI-0 and calibration packages) must
still verify hash-for-hash.  This mechanically proves that prior evidence
runs are never modified by the refinement work or the new test suite.
"""

import hashlib
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS_ROOT = os.path.join(HERE, "..", "runs")


class TestPriorEvidenceImmutable(unittest.TestCase):
    def _sealed_dirs(self):
        if not os.path.isdir(RUNS_ROOT):
            return []
        return [name for name in sorted(os.listdir(RUNS_ROOT))
                if os.path.isdir(os.path.join(RUNS_ROOT, name))
                and os.path.isfile(os.path.join(RUNS_ROOT, name,
                                                "sha256_manifest.txt"))]

    def test_prior_manifests_still_verify(self):
        dirs = self._sealed_dirs()
        self.assertTrue(dirs, "expected sealed run directories to exist")
        checked_files = 0
        for name in dirs:
            root = os.path.join(RUNS_ROOT, name)
            with open(os.path.join(root, "sha256_manifest.txt")) as fh:
                lines = fh.readlines()
            entries = {}
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                digest, rel = line.split("  ")
                entries[rel] = digest
            self.assertTrue(entries, f"{name}: manifest has no entries")
            for rel, digest in entries.items():
                path = os.path.join(root, rel)
                self.assertTrue(os.path.isfile(path),
                                f"{name}/{rel} missing")
                with open(path, "rb") as fh:
                    actual = hashlib.sha256(fh.read()).hexdigest()
                self.assertEqual(actual, digest,
                                 f"{name}/{rel} modified or corrupted")
                checked_files += 1
        self.assertGreater(checked_files, 0)

    def test_prior_dirs_contain_no_unmanifested_files(self):
        for name in self._sealed_dirs():
            root = os.path.join(RUNS_ROOT, name)
            with open(os.path.join(root, "sha256_manifest.txt")) as fh:
                lines = fh.readlines()
            entries = set()
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entries.add(line.split("  ")[1])
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames.sort()
                for fname in filenames:
                    rel = os.path.relpath(os.path.join(dirpath, fname),
                                          root)
                    if rel == "sha256_manifest.txt":
                        # the manifest cannot list itself (it hashes
                        # every OTHER file, including manifest.json)
                        continue
                    self.assertIn(rel, entries,
                                  f"{name}/{rel} not in its manifest")


if __name__ == "__main__":
    unittest.main()
