"""
Evidence preservation: run directories, raw artifacts, manifests.

Rules:
* A run directory is created exactly once and is never overwritten.
* Raw evidence (prompts, transcripts, submissions, environment logs,
  scores, usage) is written BEFORE any interpretation (the report).
* `sha256_manifest.txt` records the SHA-256 of every file in the package
  plus the hash of `manifest.json`, which describes the package.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional


class EvidenceError(RuntimeError):
    pass


class RunDirectory:
    """Builder-side evidence sink.  Also satisfies the arms.EvidenceSink
    protocol."""

    SUBDIRS = ("tasks", "prompts", "transcripts", "submissions",
               "environment_logs")

    def __init__(self, runs_root: str, run_id: str):
        self.run_id = run_id
        self.root = os.path.join(runs_root, run_id)
        if os.path.exists(self.root):
            raise EvidenceError(
                f"run directory already exists (never overwrite): {self.root}")
        os.makedirs(self.root, exist_ok=False)
        for sub in self.SUBDIRS:
            os.makedirs(os.path.join(self.root, sub), exist_ok=False)
        self._written: List[str] = []

    # -- generic writers -----------------------------------------------------

    def _path(self, rel: str) -> str:
        path = os.path.join(self.root, rel)
        parent = os.path.dirname(path)
        os.makedirs(parent, exist_ok=True)
        if os.path.exists(path):
            raise EvidenceError(f"refusing to overwrite artifact: {path}")
        return path

    def write_text(self, rel: str, text: str) -> str:
        path = self._path(rel)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        self._written.append(rel)
        return path

    def write_json(self, rel: str, obj: Any) -> str:
        return self.write_text(rel, json.dumps(obj, indent=2, sort_keys=True))

    # -- evidence-sink interface (used by arms) ------------------------------

    def save_prompt(self, arm: str, phase: str, session_id: str,
                    filename: str, text: str) -> None:
        self.write_text(
            os.path.join("prompts", arm, phase, session_id, filename), text)

    def save_transcript(self, arm: str, phase: str, session_id: str,
                        filename: str, obj: Dict[str, Any]) -> None:
        self.write_json(
            os.path.join("transcripts", arm, phase, session_id, filename),
            obj)

    def save_submission(self, arm: str, task_id: str, version: int,
                        program: str) -> None:
        self.write_text(
            os.path.join("submissions", arm, task_id,
                         f"v{version:03d}.om"), program)

    def save_env_log(self, arm: str, task_id: str, round_index: int,
                     obj: Dict[str, Any]) -> None:
        self.write_json(
            os.path.join("environment_logs", arm, task_id,
                         f"round_{round_index:02d}.json"), obj)

    # -- finalization --------------------------------------------------------

    def finalize(self, extra: Optional[Dict[str, Any]] = None) -> str:
        """Write manifest.json + sha256_manifest.txt; return manifest path.

        The manifest lists every non-manifest artifact with its SHA-256.
        sha256_manifest.txt additionally covers manifest.json itself (a
        file cannot hash itself inside itself, so the two special files
        are not self-listed)."""
        files: List[Dict[str, Any]] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames.sort()
            for name in sorted(filenames):
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, self.root)
                with open(path, "rb") as fh:
                    digest = hashlib.sha256(fh.read()).hexdigest()
                files.append({
                    "path": rel,
                    "sha256": digest,
                    "size_bytes": os.path.getsize(path),
                })
        manifest = {
            "run_id": self.run_id,
            "created_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                         time.gmtime()),
            "files": files,
        }
        if extra:
            manifest["extra"] = extra
        manifest_path = self.write_json("manifest.json", manifest)
        with open(manifest_path, "rb") as fh:
            manifest_hash = hashlib.sha256(fh.read()).hexdigest()
        lines = [
            "# SHA-256 manifest for the CVI-0 evidence package",
            f"# run_id: {self.run_id}",
            f"# manifest.json sha256: {manifest_hash}",
            "",
        ]
        all_files = list(files) + [{
            "path": "manifest.json",
            "sha256": manifest_hash,
            "size_bytes": os.path.getsize(manifest_path),
        }]
        for f in sorted(all_files, key=lambda f: f["path"]):
            lines.append(f"{f['sha256']}  {f['path']}")
        self.write_text("sha256_manifest.txt", "\n".join(lines) + "\n")
        return manifest_path


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()
