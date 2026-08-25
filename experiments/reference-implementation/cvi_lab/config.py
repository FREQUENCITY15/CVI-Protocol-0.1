"""
Pilot configuration: pinned model config, protocol constants, seeds,
budgets.  Everything the pilot needs to be reproducible and auditable.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

PILOT_VERSION = "1.1.0"
PROTOCOL_LABEL = "CVI-0.1-pilot"


@dataclass
class ModelConfig:
    provider: str = "deepseek-official"
    endpoint: str = "https://api.deepseek.com/anthropic/v1"
    api_style: str = "anthropic"
    model: str = "deepseek-v4-pro"
    temperature: float = 0.0
    seed: Optional[int] = None  # not supported by the anthropic-style endpoint
    thinking_disabled: bool = True  # pinned: deterministic text-only output
    max_tokens_per_call: int = 6000
    timeout_s: int = 600
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PilotConfig:
    version: str = PILOT_VERSION
    k: int = 4                     # Family-A tasks (pilot size)
    r: int = 3                     # revision rounds (C / S')
    tier: int = 2                  # legacy generator difficulty tier
    model: ModelConfig = field(default_factory=ModelConfig)
    # Fresh deterministic seeds for CVI-0.1.  Family C seeds are drawn
    # only after the interaction phase has completed.  Calibration seeds
    # live in a DISJOINT namespace below (asserted mechanically before any
    # official run).  CVI-0's seeds are kept as constants purely for the
    # no-reuse assertion; they are never used for generation here.
    seed_family_a: int = 20260818_001
    seed_family_b: int = 20260818_002
    seed_family_c: int = 20260818_003
    seed_calibration_base: int = 20260818_100
    seed_calibration_max: int = 20260818_999
    # CVI-0 seed namespace (evidence-only; CVI-0.1 must not draw from it)
    cvi0_seed_family_a: int = 20260817_001
    cvi0_seed_family_b: int = 20260817_002
    cvi0_seed_family_c: int = 20260817_003
    cvi0_seed_calibration_base: int = 20260817_100
    # Runaway protection
    max_total_calls: int = 60
    max_total_input_tokens: int = 300_000
    max_total_output_tokens: int = 300_000
    # Evidence
    project_root: str = field(default="")
    runs_dir: str = field(default="runs")

    def __post_init__(self) -> None:
        if not self.project_root:
            self.project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))

    def official_seeds(self) -> Dict[str, int]:
        return {"family_a": self.seed_family_a,
                "family_b": self.seed_family_b,
                "family_c": self.seed_family_c}

    def cvi0_seeds(self) -> Dict[str, int]:
        return {"family_a": self.cvi0_seed_family_a,
                "family_b": self.cvi0_seed_family_b,
                "family_c": self.cvi0_seed_family_c,
                "calibration_base": self.cvi0_seed_calibration_base}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PilotConfig":
        d = dict(d)
        model_d = d.pop("model", {})
        return cls(model=ModelConfig(**model_d), **d)


DEFAULT_CONFIG = PilotConfig()
DEFAULT_MODEL = ModelConfig()
