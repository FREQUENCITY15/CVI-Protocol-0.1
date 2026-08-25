#!/usr/bin/env python3
"""
CVI-0.1 pilot runner (refinement pilot — second engineering run).

Commands:
  python3 run_pilot.py selftest      run the deterministic local test suite
  python3 run_pilot.py calibrate     CVI-0.1 difficulty calibration
                                     (per-instance strata; selection rules
                                     in cvi_lab/calibration.py)
  python3 run_pilot.py run           run the official one-model pilot
                                     (refuses unless calibration accepted)
  python3 run_pilot.py finalize DIR  seal the evidence package

Rules enforced here:
  * the paid model is never called before the deterministic suite passes;
  * the official run refuses to start unless calibration produced an
    accepted selection (status recorded in the sealed calibration package
    and in runs/CVI-0.1_calibration_selection.json);
  * calibration seeds and official seeds come from disjoint namespaces and
    are asserted disjoint (also from the CVI-0 namespace) at run time;
  * every arm's Phase-0 baseline uses the SAME shared prompt path; the
    prompt hashes are recorded and their equality is asserted;
  * Family C is generated only after every interaction phase has completed;
  * every calibration run and every pilot run is preserved, never
    overwritten; a runaway guard stops the participant phase safely and
    still preserves all evidence collected so far.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cvi_lab import arms, calibration, generator, metrics  # noqa: E402
from cvi_lab import ordermachine as om  # noqa: E402
from cvi_lab.config import ModelConfig, PilotConfig  # noqa: E402
from cvi_lab.evidence import RunDirectory  # noqa: E402
from cvi_lab.participant import (DeepSeekAnthropicClient,  # noqa: E402
                                 RunawayGuardError, UsageTracker)
from cvi_lab.protocol import PilotProtocol  # noqa: E402

CALIBRATION_SELECTION_POINTER = "CVI-0.1_calibration_selection.json"
CALIBRATION_BAND = calibration.BAND

# One-shot heading shared by every arm's retention/transfer/hidden legs
# and by the transfer-calibration batches.
ONE_SHOT_HEADING = (
    "Attempt each of the following tasks ONE time. Write one OrderMachine "
    "program per task. You will receive no feedback.")


# ---------------------------------------------------------------------------
# API key (held in memory only; never written to disk by this runner)
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    env_key = os.environ.get("CVI_DEEPSEEK_API_KEY", "").strip()
    if env_key:
        return env_key
    cred_path = os.path.expanduser("~/.dsh/.credentials.yaml")
    if os.path.isfile(cred_path):
        text = open(cred_path).read()
        m = re.search(r"DEEPSEEK_API_KEY:\s*[\"']?([A-Za-z0-9_\-\.]+)",
                      text)
        if m:
            return m.group(1)
    raise RuntimeError(
        "no DeepSeek API key found: set CVI_DEEPSEEK_API_KEY or place the "
        "harness credential at ~/.dsh/.credentials.yaml")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> "tuple[int, str]":
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=HERE, capture_output=True, text=True, timeout=600)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def require_selftest() -> str:
    code, output = run_selftest()
    if code != 0:
        print("DETERMINISTIC SELF-TEST FAILED — refusing to call the paid "
              "model. Fix the implementation and rerun.\n")
        print(output)
        sys.exit(1)
    return output


# ---------------------------------------------------------------------------
# Calibration (CVI-0.1: per-instance strata, documented selection rules)
# ---------------------------------------------------------------------------

def _score_batch(client, tasks, cfg, sink, label, shared_baseline=True):
    """Score one batch of tasks with the pinned model.

    shared_baseline=True uses the SAME Phase-0 prompt path as the official
    arms (build_baseline_prompt); otherwise the shared one-shot heading.
    Each batch gets a distinct evidence arm label so its session/artifact
    paths can never collide inside the calibration package."""
    runner = arms.ArmRunner(f"CAL-{label}", client, cfg, sink)
    if shared_baseline:
        runner.run_phase_0(tasks)
        record = runner.result["phase_0"]
    else:
        session = runner.new_session("calibration")
        record = runner.one_shot(session, tasks, ONE_SHOT_HEADING, label)
        record["session_id"] = session.session_id
    result = runner.finish()
    scores = [entry["hidden_score"] for entry in record["tasks"].values()]
    return scores, record, result


def run_calibration(cfg: PilotConfig, api_key: str,
                    resume_dir: str = None) -> int:
    """CVI-0.1 calibration: baseline strata + transfer levels, all
    disposable seeds, all records preserved, selection rules applied in
    code (cvi_lab/calibration.py).

    `resume_dir`: import the SEALED baseline records from a previous
    calibration run directory (no new baseline participant calls); the
    selection rule is re-applied to the imported records."""
    require_selftest()
    runs_root = os.path.join(cfg.project_root, cfg.runs_dir)
    os.makedirs(runs_root, exist_ok=True)
    rd = RunDirectory(
        runs_root,
        f"CVI-0.1_calibration_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
    tracker = UsageTracker(cfg.max_total_calls, cfg.max_total_input_tokens,
                           cfg.max_total_output_tokens)
    client = DeepSeekAnthropicClient(cfg.model, tracker, api_key)

    rd.write_json("config.json", {
        "pilot_config": cfg.to_dict(),
        "calibration": {
            "rule_version": calibration.RULE_VERSION,
            "baseline_catalog": calibration.BASELINE_CATALOG,
            "transfer_s3_levels": calibration.TRANSFER_S3_LEVELS,
            "band": list(CALIBRATION_BAND),
            "transfer_s3_ceiling": calibration.TRANSFER_S3_CEILING,
            "baseline_replicates": calibration.BASELINE_REPLICATES,
            "transfer_replicates": calibration.TRANSFER_REPLICATES,
        }})
    rd.write_text("prompts/spec_sheet.md", om.PARTICIPANT_SPEC)

    seeds_used: dict = {"baseline": [], "transfer_a": [], "transfer_b": []}

    # ---- 1. Baseline strata ------------------------------------------------
    baseline_records: dict = {"instances": [], "batches": []}
    if resume_dir:
        source_root = os.path.join(runs_root, resume_dir)
        source_path = os.path.join(source_root, "selection.json")
        if not os.path.isfile(source_path):
            raise RuntimeError(
                f"--resume: no sealed selection.json in {source_root}")
        source = json.load(open(source_path))
        baseline_records = dict(source.get("baseline", {}))
        baseline_records["imported_from"] = resume_dir
        baseline_records["import_note"] = (
            "baseline records imported from the sealed calibration package "
            "(no new baseline participant calls); the selection rule was "
            f"re-applied at rule_version {calibration.RULE_VERSION}")
        seeds_used["baseline"] = list(
            source.get("seeds_used", {}).get("baseline", []))
        print(f"baseline records imported from {resume_dir}")
    else:
        try:
            for rep in range(1, calibration.BASELINE_REPLICATES + 1):
                seed = cfg.seed_calibration_base + rep
                seeds_used["baseline"].append(seed)
                tasks = generator.generate_stratified_calibration_batch(
                    calibration.BASELINE_CATALOG, seed)
                rd.write_json(f"tasks/baseline_batch_{rep}.json",
                              [t.to_dict() for t in tasks])
                scores, record, result = _score_batch(
                    client, tasks, cfg, rd, f"cal_baseline_{rep}",
                    shared_baseline=True)
                calibration.record_baseline_instances(
                    baseline_records["instances"], rep, zip(tasks, scores))
                baseline_records["batches"].append({
                    "batch": rep, "seed": seed,
                    "scores": {t.task_id: s for t, s in zip(tasks, scores)},
                    "S0_batch": (sum(scores) / len(scores)) if scores else None})
                rd.write_json(f"scores/baseline_batch_{rep}.json",
                              baseline_records["batches"][-1])
                print(f"baseline calibration batch {rep}: "
                      f"S0={baseline_records['batches'][-1]['S0_batch']:.3f}")
        except RunawayGuardError as exc:
            rd.write_text("RUNAWAY_GUARD_TRIGGERED.txt",
                          f"RUNAWAY_GUARD_TRIGGERED during calibration: {exc}\n"
                          "Evidence preserved below.")
            rd.write_json("api_usage.json", tracker.to_dict())
            rd.finalize({"status": "runaway_guard_triggered"})
            print(f"RUNAWAY_GUARD_TRIGGERED during calibration; evidence "
                  f"preserved in {rd.root}")
            return 2

    baseline_selection = calibration.select_baseline_spec(baseline_records)
    baseline_records["selection"] = baseline_selection
    print(f"baseline selection: status={baseline_selection['status']} "
          f"predicted S0={baseline_selection['predicted_s0']} "
          f"spec={baseline_selection['spec']}")

    # ---- 2. Transfer strata ------------------------------------------------
    transfer_records: dict = {"attempts": []}
    transfer_selection: dict = {"status": "needs_refinement", "attempts": []}
    if baseline_selection["status"] == "accepted":
        spec = baseline_selection["spec"]
        for level_idx, level in enumerate(
                calibration.TRANSFER_S3_LEVELS[
                    :calibration.MAX_TRANSFER_LEVELS]):
            attempt = {"level": level_idx, "level_spec": dict(level),
                       "s_tr_batches": [], "s3_batches": [],
                       "instances": []}
            for rep in range(1, calibration.TRANSFER_REPLICATES + 1):
                a_seed = cfg.seed_calibration_base + 100 + 20 * level_idx + rep
                b_seed = cfg.seed_calibration_base + 110 + 20 * level_idx + rep
                seeds_used["transfer_a"].append(a_seed)
                seeds_used["transfer_b"].append(b_seed)
                cal_a = generator.generate_family_a(
                    4, a_seed, spec=spec, id_prefix="CAL-A")
                cal_b = generator.generate_family_b(
                    cal_a, b_seed, spec=spec, s3_spec=level)
                rd.write_json(
                    f"tasks/transfer_batch_{level_idx}_{rep}_a.json",
                    [t.to_dict() for t in cal_a])
                rd.write_json(
                    f"tasks/transfer_batch_{level_idx}_{rep}_b.json",
                    [t.to_dict() for t in cal_b])
                scores, record, result = _score_batch(
                    client, cal_b, cfg, rd,
                    f"cal_transfer_L{level_idx}_r{rep}",
                    shared_baseline=False)
                s_tr = (sum(scores) / len(scores)) if scores else None
                s3_ids = [t.task_id for t in cal_b
                          if t.subfamily == "s3"]
                s3_scores = [s for t, s in zip(cal_b, scores)
                             if t.task_id in s3_ids]
                s3 = (sum(s3_scores) / len(s3_scores)) if s3_scores else None
                attempt["s_tr_batches"].append(s_tr)
                attempt["s3_batches"].append(s3)
                for t, s in zip(cal_b, scores):
                    attempt["instances"].append({
                        "batch": rep, "task_id": t.task_id,
                        "subfamily": t.subfamily, "recipe": t.recipe,
                        "stratum_key": t.difficulty["stratum_key"],
                        "seed": t.seed, "checksum": t.checksum(),
                        "score": s})
                rd.write_json(
                    f"scores/transfer_batch_{level_idx}_{rep}.json", {
                        "batch": rep, "seed_a": a_seed, "seed_b": b_seed,
                        "s_tr": s_tr, "s3": s3,
                        "scores": {t.task_id: s
                                   for t, s in zip(cal_b, scores)}})
            attempt["s_tr_mean"] = calibration.mean(attempt["s_tr_batches"])
            attempt["s3_mean"] = calibration.mean(attempt["s3_batches"])
            transfer_records["attempts"].append(attempt)
            print(f"transfer calibration level {level_idx}: "
                  f"S_tr={attempt['s_tr_mean']} "
                  f"S3={attempt['s3_mean']}")
            decision = calibration.select_transfer_level(
                transfer_records["attempts"])
            if decision["status"] == "accepted":
                break
        transfer_selection = calibration.select_transfer_level(
            transfer_records["attempts"])
    transfer_records["selection"] = transfer_selection

    status = "accepted" if (
        baseline_selection["status"] == "accepted"
        and transfer_selection["status"] == "accepted") else "needs_refinement"

    selection_doc = {
        "status": status,
        "rule_version": calibration.RULE_VERSION,
        "band": list(CALIBRATION_BAND),
        "transfer_s3_ceiling": calibration.TRANSFER_S3_CEILING,
        "baseline": baseline_records,
        "transfer": transfer_records,
        "seeds_used": {k: sorted(v) for k, v in seeds_used.items()},
        "note": ("Calibration runs are pilot engineering evidence, not CVI "
                 "results.  The selection rules are fixed in "
                 "cvi_lab/calibration.py and were applied in code."),
        "created_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    rd.write_json("selection.json", selection_doc)
    rd.write_json("api_usage.json", tracker.to_dict())
    rd.finalize({"status": status})

    pointer_path = os.path.join(runs_root, CALIBRATION_SELECTION_POINTER)
    with open(pointer_path, "w") as fh:
        json.dump({"calibration_dir": rd.run_id, "status": status,
                   "selection": selection_doc}, fh, indent=2, sort_keys=True)
    print(json.dumps(selection_doc, indent=2))
    if status != "accepted":
        print("CALIBRATION STATUS: needs_refinement — the official CVI-0.1 "
              "run is REFUSED until a usable range is demonstrated. "
              "Evidence preserved.")
    return 0


# ---------------------------------------------------------------------------
# Pilot
# ---------------------------------------------------------------------------

def load_calibration_selection(cfg: PilotConfig) -> dict:
    path = os.path.join(cfg.project_root, cfg.runs_dir,
                        CALIBRATION_SELECTION_POINTER)
    if not os.path.isfile(path):
        raise RuntimeError(
            f"no calibration selection found at {path} — run "
            f"`python3 run_pilot.py calibrate` first (the official run "
            f"refuses to start without an accepted calibration)")
    doc = json.load(open(path))
    if doc.get("status") != "accepted":
        raise RuntimeError(
            f"calibration selection status={doc.get('status')} — the "
            f"official run refuses to start")
    return doc


def assert_seed_disjointness(cfg: PilotConfig, selection: dict) -> None:
    official = list(cfg.official_seeds().values())
    cal_namespace = range(cfg.seed_calibration_base,
                          cfg.seed_calibration_max + 1)
    cvi0_seeds = list(cfg.cvi0_seeds().values())
    for s in official:
        if s in cal_namespace:
            raise RuntimeError(
                f"official seed {s} inside calibration namespace")
    used_cal = []
    for k, v in selection.get("seeds_used", {}).items():
        used_cal.extend(v)
    overlap = set(official) & set(used_cal)
    if overlap:
        raise RuntimeError(
            f"official seeds collide with calibration seeds: {overlap}")
    overlap_cvi0 = set(official) & set(cvi0_seeds)
    if overlap_cvi0:
        raise RuntimeError(
            f"official seeds collide with the CVI-0 namespace: "
            f"{overlap_cvi0}")


def run_pilot(cfg: PilotConfig, api_key: str) -> int:
    selftest_output = require_selftest()
    pointer = load_calibration_selection(cfg)
    selection = pointer["selection"]
    spec = selection["baseline"]["selection"]["spec"]
    s3_spec = selection["transfer"]["selection"]["s3_spec"]
    assert_seed_disjointness(cfg, selection)

    runs_root = os.path.join(cfg.project_root, cfg.runs_dir)
    os.makedirs(runs_root, exist_ok=True)
    run_id = f"CVI-0.1_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    rd = RunDirectory(runs_root, run_id)
    tracker = UsageTracker(cfg.max_total_calls, cfg.max_total_input_tokens,
                           cfg.max_total_output_tokens)
    client = DeepSeekAnthropicClient(cfg.model, tracker, api_key)
    protocol = PilotProtocol()
    started = time.monotonic()

    rd.write_text("prompts/spec_sheet.md", om.PARTICIPANT_SPEC)
    rd.write_json("config.json", {
        "pilot_config": cfg.to_dict(),
        "run_id": run_id,
        "calibration_source": pointer.get("calibration_dir"),
        "started_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    rd.write_json("calibration_selection.json", selection)

    # Family A + B exist before any participant session.  Fresh official
    # seeds; instances drawn from the calibration-selected strata.
    tasks_a = generator.generate_family_a(cfg.k, cfg.seed_family_a,
                                          tier=cfg.tier, spec=spec)
    tasks_b = generator.generate_family_b(tasks_a, cfg.seed_family_b,
                                          tier=cfg.tier, spec=spec,
                                          s3_spec=s3_spec)
    rd.write_json("tasks/family_a.json", [t.to_dict() for t in tasks_a])
    rd.write_json("tasks/family_b.json", [t.to_dict() for t in tasks_b])
    rd.write_json("tasks/difficulty_summary.json", {
        "family_a": {t.task_id: {
            "stratum_key": t.difficulty["stratum_key"],
            "features": t.difficulty["features"]}
            for t in tasks_a},
        "family_b": {t.task_id: {
            "stratum_key": t.difficulty["stratum_key"],
            "features": t.difficulty["features"]}
            for t in tasks_b},
    })
    rd.write_json("seeds.json", {
        "master_seeds": {
            "family_a": cfg.seed_family_a,
            "family_b": cfg.seed_family_b,
            "family_c": cfg.seed_family_c,
        },
        "tier": cfg.tier,
        "baseline_spec": spec,
        "s3_spec": s3_spec,
        "calibration_seeds_used": selection.get("seeds_used", {}),
        "cvi0_seed_namespace": cfg.cvi0_seeds(),
        "seed_disjointness": "verified by assert_seed_disjointness()",
        "family_a_checksum": generator.tasks_checksum(tasks_a),
        "family_b_checksum": generator.tasks_checksum(tasks_b),
        "task_seeds": [
            {"task_id": t.task_id, "seed": t.seed, "case_seed": t.case_seed}
            for t in tasks_a + tasks_b],
    })

    arm_pre = {
        "S": arms.run_arm_s_pre,
        "S_PRIME": arms.run_arm_sprime_pre,
        "C": arms.run_arm_c_pre,
    }
    runners = {}
    arm_results = {}
    current_arm = None
    current_runner = None
    try:
        # Phase 0 baseline + Phase 1/1' + retention + transfer, arm by arm,
        # isolated sessions.
        for arm_name, pre_fn in arm_pre.items():
            current_arm = arm_name
            protocol.event("arm_pre_start", arm=arm_name)
            current_runner = pre_fn(client, cfg, rd, tasks_a, tasks_b)
            runners[arm_name] = current_runner
            arm_results[arm_name] = current_runner.result
            protocol.event("arm_pre_done", arm=arm_name)
            rd.write_json(f"scores_partial_{arm_name}.json", {
                "arm": arm_name, "result": current_runner.result,
                "api_usage": tracker.to_dict()})

        # Baseline prompt identity: mechanically required to be identical
        # across arms (Refinement 1).  Record the hashes; abort on any
        # divergence (protocol deviation) so evidence is preserved intact.
        baseline_hashes = {
            arm: runners[arm].result["phase_0_prompt_sha256"]
            for arm in runners}
        identical = len(set(baseline_hashes.values())) == 1
        rd.write_json("prompt_hashes.json", {
            "phase_0_user_prompt_sha256": baseline_hashes,
            "phase_0_prompt_bytes_identical_across_arms": identical,
            "shared_baseline_heading": arms.BASELINE_HEADING,
            "system_prompt_sha256": hashlib.sha256(
                arms.build_system_prompt(om.PARTICIPANT_SPEC)
                .encode("utf-8")).hexdigest(),
        })
        if not identical:
            raise RuntimeError(
                "PROTOCOL DEVIATION: Phase-0 baseline prompt bytes differ "
                "across arms — refusing to continue")

        protocol.mark_interaction_complete()

        # ONLY NOW: hidden verification family, fresh seeds.
        tasks_c = protocol.generate_family_c(seed=cfg.seed_family_c,
                                             tier=cfg.tier, spec=spec)
        rd.write_json("tasks/family_c.json", [t.to_dict() for t in tasks_c])
        rd.write_json("tasks/difficulty_summary_family_c.json", {
            t.task_id: {"stratum_key": t.difficulty["stratum_key"],
                        "features": t.difficulty["features"]}
            for t in tasks_c})
        rd.write_json("seeds_family_c.json", {
            "family_c_checksum": generator.tasks_checksum(tasks_c),
            "task_seeds": [
                {"task_id": t.task_id, "seed": t.seed,
                 "case_seed": t.case_seed} for t in tasks_c],
            "generated_after_interaction_iso":
                protocol.log.family_c_generated_iso})
        protocol.event("arm_hidden_start")
        for arm_name, runner in runners.items():
            current_arm = arm_name
            current_runner = runner
            runner.run_hidden_probe(tasks_c)
            arm_results[arm_name] = runner.finish()
            protocol.event("arm_hidden_done", arm=arm_name)
    except RunawayGuardError as exc:
        if current_runner is not None and current_arm is not None:
            arm_results[current_arm] = current_runner.result
        rd.write_text("RUNAWAY_GUARD_TRIGGERED.txt",
                      f"RUNAWAY_GUARD_TRIGGERED: {exc}\n"
                      "The participant phase was stopped safely; all "
                      "evidence collected so far is preserved below.")
        rd.write_json("api_usage.json", tracker.to_dict())
        rd.write_json("scores_partial.json", {"arms": arm_results})
        rd.finalize({"status": "runaway_guard_triggered"})
        print(f"RUNAWAY_GUARD_TRIGGERED: {exc}")
        print(f"evidence preserved in {rd.root}")
        return 2
    except RuntimeError as exc:
        rd.write_text("PROTOCOL_DEVIATION.txt",
                      f"PROTOCOL DEVIATION: {exc}\n"
                      "The run was stopped; evidence preserved below.")
        rd.write_json("api_usage.json", tracker.to_dict())
        rd.write_json("scores_partial.json", {"arms": arm_results})
        rd.finalize({"status": "protocol_deviation"})
        print(f"PROTOCOL DEVIATION: {exc}")
        print(f"evidence preserved in {rd.root}")
        return 2

    elapsed = time.monotonic() - started
    # Measurement vector
    tasks_b_by_sub = {}
    for t in tasks_b:
        tasks_b_by_sub.setdefault(t.subfamily, []).append(t.task_id)
    pilot_metrics = metrics.compute_pilot_metrics(
        arms=arm_results,
        tasks_a=[t.task_id for t in tasks_a],
        tasks_b_by_sub=tasks_b_by_sub,
        tasks_c=[t.task_id for t in tasks_c],
        api_usage=tracker.to_dict())

    rd.write_json("scores.json", {"arms": arm_results})
    rd.write_json("metrics.json", pilot_metrics)
    rd.write_json("api_usage.json", tracker.to_dict())
    rd.write_json("protocol.json", protocol.to_dict())
    rd.write_json("elapsed.json", {"total_seconds": round(elapsed, 3),
                                   "started_iso": protocol.log.started_iso,
                                   "ended_iso": time.strftime(
                                       "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    print(f"PILOT DATA COLLECTION COMPLETE — raw evidence: {rd.root}")
    print("Next: compose CVI_0_1_Pilot_Report.md, then run "
          f"`python3 run_pilot.py finalize {run_id}` to seal the package.")
    _print_summary(pilot_metrics, tracker, rd.root)
    return 0


def finalize_run(cfg: PilotConfig, run_id: str, report_path: str) -> int:
    """Copy the pilot report into the evidence package and hash
    everything.  Raw evidence is written before interpretation; the
    manifest is generated only now, last."""
    if not os.path.isfile(report_path):
        print(f"report not found: {report_path}")
        return 1
    runs_root = os.path.join(cfg.project_root, cfg.runs_dir)
    root = os.path.join(runs_root, run_id)
    if not os.path.isdir(root):
        print(f"run directory not found: {root}")
        return 1
    report_md = open(report_path, encoding="utf-8").read()
    rd = RunDirectory.__new__(RunDirectory)  # reopen, not create
    rd.root = root
    rd.run_id = run_id
    rd._written = []
    rd.write_text("pilot_report.md", report_md)
    manifest_path = rd.finalize({"status": "complete"})
    print(f"evidence package sealed: {root}")
    print(f"manifest: {manifest_path}")
    return 0


def _print_summary(pilot_metrics, tracker, root):
    for arm, m in pilot_metrics["arms"].items():
        print(f"  {arm}: S0={m['S0']} S_post={m['S_post']} "
              f"S_ret={m['S_ret']} S_tr={m['S_tr']} S_ver={m['S_ver']}")
    u = tracker.to_dict()
    print(f"  API: calls={u['calls']} in={u['input_tokens']} "
          f"out={u['output_tokens']} cache_read={u['cache_read_tokens']}")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="CVI-0.1 pilot runner")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest", help="run the deterministic local test suite")
    p_cal = sub.add_parser("calibrate", help="CVI-0.1 difficulty calibration")
    p_cal.add_argument("--resume", default=None,
                       help="import sealed baseline records from a previous "
                            "calibration run directory (no new baseline "
                            "participant calls)")
    p_run = sub.add_parser("run", help="run the official CVI-0.1 pilot")
    p_fin = sub.add_parser("finalize", help="seal the evidence package")
    p_fin.add_argument("run_id", help="run directory name under runs/")
    p_fin.add_argument(
        "--report",
        default=os.path.join(HERE, "CVI_0_1_Pilot_Report.md"),
        help="path to the pilot report to seal in")
    args = parser.parse_args()

    cfg = PilotConfig()
    if args.command == "selftest":
        code, output = run_selftest()
        print(output)
        return code
    try:
        if args.command == "calibrate":
            return run_calibration(cfg, load_api_key(),
                                   resume_dir=args.resume)
        if args.command == "run":
            return run_pilot(cfg, load_api_key())
        if args.command == "finalize":
            return finalize_run(cfg, args.run_id, args.report)
    except RuntimeError as exc:
        print(f"refusing to proceed: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
