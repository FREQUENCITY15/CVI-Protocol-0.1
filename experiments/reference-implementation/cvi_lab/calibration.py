"""
CVI-0.1 difficulty calibration: deterministic per-instance strata and the
SELECTION RULES applied to calibration evidence.

THE SELECTION RULES (fixed in code BEFORE any calibration call was made;
no instance of task selection depends on any arm's comparative outcome):

1. BASELINE (Phase 0).  Every Family-A recipe has a deterministic stratum
   catalog (BASELINE_CATALOG): each stratum pins the recipe's parameter
   draw (k / m / mode).  Calibration generates one disposable instance
   per (recipe, stratum) entry per replicate batch and scores it one-shot
   with the pinned participant model using the SAME shared Phase-0 prompt
   path as the official run.
     * A family SPEC is one stratum per recipe.
     * Specs are enumerated in fixed order (recipe order x catalog index).
     * Predicted S0 of a spec = mean of the calibration scores of its
       selected strata (each stratum's score = mean over its calibration
       instances).
     * SELECT: the FIRST spec whose predicted FAMILY S0 lies in
       [0.30, 0.80] — the design's own band criterion is family-level.
     * Strata whose mean falls outside the band are FLAGGED (recorded
       observation with their scores), not silently dropped: the CVI-0.1
       baseline-calibration evidence showed this model's difficulty is
       recipe-degenerate (whole recipes at 0.0 or 1.0 while the parameter
       strata inside a recipe do not modulate the score), so requiring
       every stratum to be individually in-band is unsatisfiable by
       construction.  A flagged stratum is exactly the recorded
       structural observation refinement 2 asks for.
     * If no spec's predicted family S0 is in band: select the spec whose
       predicted S0 is CLOSEST to the band, mark it a fallback and record
       the reason.  The official run REFUSES to start unless the
       selection is accepted.

2. TRANSFER (Family B).  S3 parameter levels in fixed order
   (TRANSFER_S3_LEVELS).  Level 0 is the CVI-0.1 default (nested/queue
   compositions replacing CVI-0's S3, which sat at ceiling).  For each
   level, calibration generates a disposable Family A (from the accepted
   baseline spec) and a disposable Family B (S1/S2 derived from that A;
   S3 from the level spec) and scores it one-shot, 2 replicate batches.
     * Accept the FIRST level whose observed S_tr (mean over replicate
       batches) lies in [0.30, 0.80] AND whose S3 subfamily mean is below
       0.90 (no ceiling).
     * A rejected level's reason is recorded (saturated above band, below
       band, or S3 ceiling) and its instances remain preserved.
     * If no level is accepted, status = NEEDS_REFINEMENT and the official
       run is refused.

3. DISJOINTNESS.  Calibration seeds live in
   cfg.seed_calibration_base .. cfg.seed_calibration_max.  Official seeds
   are cfg.seed_family_a/b/c.  The disjointness of these namespaces and of
   every generated instance checksum is asserted mechanically (tests +
   run-time gate).  No calibration instance ever appears in CVI-0.1, and
   no CVI-0 instance is reused (CVI-0 seed constants are recorded for the
   assertion only).

RULE HISTORY (recorded so the selection is auditable):
  * rule 1.0: a spec was accepted only when EVERY selected stratum mean
    lay in the band.  Applied to calibration batch 1
    (CVI-0.1_calibration_20260817T212849Z): unsatisfiable — the model's
    per-instance scores were recipe-degenerate (mirror_add 0.0 on 6/6
    instances; swizzle_mul, swizzle_mul_add, splice_drain 1.0 on 24/24),
    so no spec could satisfy it even though the family composition
    predicts S0 = 0.75, inside the design band.  Rule 1.0's fallback was
    preserved as sealed calibration evidence.
  * rule 1.1 (this module): family-level band criterion + flagged
    degenerate strata, applied to the SAME sealed records (no new
    baseline calls; the records are imported, not regenerated).

Calibration data is pilot engineering evidence, never CVI results.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Tuple

RULE_VERSION = "1.1"
BAND = (0.30, 0.80)
TRANSFER_S3_CEILING = 0.90
BASELINE_REPLICATES = 2
TRANSFER_REPLICATES = 2
MAX_TRANSFER_LEVELS = 3

# One stratum per (recipe, param pin).  Ordered easy -> harder surface.
BASELINE_CATALOG: Dict[str, Tuple[Dict[str, Any], ...]] = {
    "swizzle_mul": ({"k": 2}, {"k": 3}, {"k": 5}),
    "mirror_add": ({"k": 2}, {"k": 4}, {"k": 7}),
    "swizzle_mul_add": ({"k": 2, "m": 1}, {"k": 3, "m": 2}, {"k": 4, "m": 3}),
    "splice_drain": ({"mode": "drain"}, {"mode": "discard_front"}),
}

# Transfer S3 levels, fixed order.  CVI-0's helix_mul_add / nudge_add S3
# batch sat at ceiling (S_tr = 1.0 for all arms), so it is deliberately
# NOT part of the catalog; levels start at the harder nested/queue
# compositions.
TRANSFER_S3_LEVELS: Tuple[Dict[str, Dict[str, Any]], ...] = (
    {"fold_helix_add": {"k": 2}, "helix_push_drain": {"k": 1}},
    {"fold_helix_add": {"k": 3}, "helix_push_drain": {"k": 2}},
    {"fold_helix_add": {"k": 5}, "helix_push_drain": {"k": 4}},
)


def _mean(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def mean(values: List[float]) -> Optional[float]:
    """Public mean helper used by the calibration runner."""
    return _mean(values)


def _in_band(value: Optional[float]) -> bool:
    return value is not None and BAND[0] <= value <= BAND[1]


def band_distance(value: Optional[float]) -> float:
    """Distance of a score from the band (0.0 when inside)."""
    if value is None:
        return float("inf")
    if value < BAND[0]:
        return BAND[0] - value
    if value > BAND[1]:
        return value - BAND[1]
    return 0.0


def enumerate_specs() -> List[Dict[str, Dict[str, Any]]]:
    """All (one stratum per recipe) specs in fixed deterministic order."""
    recipes = list(BASELINE_CATALOG.keys())
    index_ranges = [range(len(BASELINE_CATALOG[r])) for r in recipes]
    specs = []
    for combo in itertools.product(*index_ranges):
        specs.append({recipe: dict(BASELINE_CATALOG[recipe][idx])
                      for recipe, idx in zip(recipes, combo)})
    return specs


def _stratum_key(recipe: str, stratum: Dict[str, Any]) -> str:
    parts = [recipe]
    for key in ("k", "m", "mode"):
        if key in stratum:
            parts.append(f"[{key}={stratum[key]}]")
    parts.append("[phr=1]")
    return "".join(parts)


def select_baseline_spec(records: Dict[str, Any]) -> Dict[str, Any]:
    """Apply baseline selection rule 1.1 to the calibration records.

    `records` must contain `instances`: a list of
    {"recipe": ..., "stratum": {...}, "stratum_key": ..., "score": ...}.
    A spec (one stratum per recipe) is ACCEPTED when its predicted FAMILY
    S0 (mean of the selected strata's calibration means) lies in the
    band.  Strata whose own mean falls outside the band are FLAGGED as
    recorded observations (see module docstring, rule history).  Specs
    are enumerated in fixed order; the first accepted spec wins.
    Returns {"status": "accepted"|"fallback", "spec": {...},
             "predicted_s0": ..., "per_stratum_s0": {...},
             "flagged_strata": {...}, "reason": ...}.
    """
    instances = records.get("instances", [])
    scores_by_stratum: Dict[str, List[float]] = {}
    for inst in instances:
        key = inst["stratum_key"]
        scores_by_stratum.setdefault(key, []).append(float(inst["score"]))
    stratum_mean = {key: _mean(v) for key, v in scores_by_stratum.items()}

    def spec_stratum_means(spec: Dict[str, Dict[str, Any]]
                           ) -> Dict[str, Optional[float]]:
        return {recipe: stratum_mean.get(_stratum_key(recipe, stratum))
                for recipe, stratum in spec.items()}

    specs = enumerate_specs()
    best = None
    best_distance = float("inf")
    for spec in specs:
        means = spec_stratum_means(spec)
        predicted = _mean([m for m in means.values() if m is not None])
        flagged_strata = {recipe: m for recipe, m in means.items()
                          if m is not None and not _in_band(m)}
        if _in_band(predicted):
            return {"status": "accepted", "spec": spec,
                    "predicted_s0": predicted,
                    "per_stratum_s0": means,
                    "flagged_strata": {
                        recipe: {"stratum_mean": m,
                                 "note": ("stratum outside band: recorded "
                                          "structural observation "
                                          "(recipe-degenerate difficulty)")}
                        for recipe, m in flagged_strata.items()},
                    "reason": (f"first spec (fixed enumeration order) with "
                               f"predicted family S0 {predicted:.3f} in "
                               f"band {BAND}")}
        distance = band_distance(predicted)
        if distance < best_distance:
            best_distance = distance
            best = {"status": "fallback", "spec": spec,
                    "predicted_s0": predicted,
                    "per_stratum_s0": means,
                    "flagged_strata": {
                        recipe: {"stratum_mean": m,
                                 "note": ("stratum outside band: recorded "
                                          "structural observation "
                                          "(recipe-degenerate difficulty)")}
                        for recipe, m in flagged_strata.items()},
                    "reason": (f"no spec's predicted family S0 landed in "
                               f"band {BAND}; this spec (predicted S0 "
                               f"{predicted:.3f}) is closest to the band "
                               f"(distance {distance:.3f})")}
    return best or {"status": "fallback", "spec": None,
                    "predicted_s0": None, "per_stratum_s0": None,
                    "flagged_strata": {},
                    "reason": "no calibration instances recorded"}


def select_transfer_level(attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply selection rule 2 to the transfer calibration attempts.

    `attempts` is an ordered list of
    {"level": i, "level_spec": {...}, "s_tr_batches": [..],
     "s3_batches": [..], "s_tr_mean": ..., "s3_mean": ...}.
    Returns {"status": "accepted"|"needs_refinement", "s3_spec": ...,
             "s_tr_mean": ..., "level": ...} plus per-attempt reasons.
    """
    for attempt in attempts:
        s_tr = attempt.get("s_tr_mean")
        s3 = attempt.get("s3_mean")
        if _in_band(s_tr) and s3 is not None and s3 < TRANSFER_S3_CEILING:
            attempt["decision"] = "accepted"
            attempt["reason"] = (
                f"S_tr {s_tr:.3f} in band {BAND} and S3 subfamily "
                f"{s3:.3f} below ceiling {TRANSFER_S3_CEILING}")
            return {"status": "accepted", "level": attempt["level"],
                    "s3_spec": attempt["level_spec"],
                    "s_tr_mean": s_tr, "s3_mean": s3,
                    "attempts": attempts}
        if s_tr is not None and s_tr > BAND[1]:
            reason = f"S_tr {s_tr:.3f} above band (saturated); escalate"
        elif s3 is not None and s3 >= TRANSFER_S3_CEILING:
            reason = f"S3 subfamily {s3:.3f} at ceiling; escalate"
        elif s_tr is not None and s_tr < BAND[0]:
            reason = f"S_tr {s_tr:.3f} below band (too hard); escalate"
        else:
            reason = "insufficient calibration evidence"
        attempt["decision"] = "rejected"
        attempt["reason"] = reason
    return {"status": "needs_refinement", "level": None, "s3_spec": None,
            "s_tr_mean": None, "s3_mean": None,
            "reason": ("no transfer level produced a usable range; the "
                       "official run must not start"),
            "attempts": attempts}


def record_baseline_instances(instances: List[Dict[str, Any]],
                              batch_index: int,
                              task_scores: List[Tuple[Any, float]]
                              ) -> None:
    """Append per-instance calibration records (task + observed score)."""
    for (task, score) in task_scores:
        instances.append({
            "batch": batch_index,
            "task_id": task.task_id,
            "recipe": task.recipe,
            "stratum": dict(task.params),
            "stratum_key": task.difficulty["stratum_key"],
            "seed": task.seed,
            "case_seed": task.case_seed,
            "checksum": task.checksum(),
            "score": score,
        })
