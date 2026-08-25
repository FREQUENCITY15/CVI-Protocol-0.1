"""
CVI-0.1 refinement tests.

Covers the three CVI-0 defects:

1. Phase-0 baseline prompt identity across S / S' / C (shared builder,
   byte-identical participant-visible prompts, independent calls, no
   treatment labels, hashes recorded).
2. Per-instance difficulty metadata: deterministic, seed-reproducible,
   recorded for every instance; calibration seeds disjoint from official
   seeds; selection rules fixed in code.
3. Transfer: Family-B instances identical across arms; new S3 recipes;
   calibration/official transfer-seed disjointness.

Plus the protocol invariants the refinement must not break (Family-C
gate, hidden-test inaccessibility, per-arm feedback rules, context
reset) — re-asserted here against the NEW phase-0 baseline structure.
"""

import hashlib
import json
import os
import re
import unittest

from cvi_lab import arms, calibration, generator as gen, grader
from cvi_lab import ordermachine as om
from cvi_lab.config import PilotConfig
from cvi_lab.participant import LLMResponse
from cvi_lab.protocol import PilotProtocol, ProtocolError

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_A = 313131
SEED_B = 414141
SEED_C = 515151
SEED_CAL = 616161


class MemorySink:
    def __init__(self):
        self.prompts = {}
        self.transcripts = {}
        self.submissions = {}
        self.env_logs = {}

    def save_prompt(self, arm, phase, session_id, filename, text):
        self.prompts[(arm, phase, filename)] = text

    def save_transcript(self, arm, phase, session_id, filename, obj):
        self.transcripts[(arm, phase, filename)] = obj

    def save_submission(self, arm, task_id, version, program):
        self.submissions[(arm, task_id, version)] = program

    def save_env_log(self, arm, task_id, round_index, obj):
        self.env_logs[(arm, task_id, round_index)] = obj


class MockClient:
    """Scripted stateless participant client; records system/messages per
    call so tests can prove prompt identity and context boundaries."""

    def __init__(self, responder):
        self.responder = responder
        self.calls = []

    def complete(self, system, messages, max_tokens, label):
        self.calls.append({
            "label": label,
            "system": system,
            "messages": json.loads(json.dumps(messages)),
        })
        text = self.responder(label, len(self.calls))
        return LLMResponse(
            text=text, model="mock", stop_reason="end_turn",
            input_tokens=10, output_tokens=len(text) // 4,
            cache_read_tokens=0, cache_creation_tokens=0, latency_s=0.0)


def _program_section(task_id, program):
    return f"### TASK {task_id}\n{program}\n### END\n"


def _naive_responder():
    """Return every requested program section as the task's naive
    misparse (deterministic, per-task)."""
    def responder(label, call_index):
        # tasks known from the enclosing scope via closure below
        return "\n".join(_program_section(tid, p)
                         for tid, p in responder.programs.items())
    return responder


def _task_sections(text):
    sections = {}
    parts = re.split(r"## Task ([A-Za-z0-9_\-]+)", text)
    for i in range(1, len(parts), 2):
        sections.setdefault(parts[i], []).append(parts[i + 1])
    return sections


def _run_three_arms():
    """Run all three arms against mock clients; return the runners and
    the clients."""
    tasks_a = gen.generate_family_a(4, SEED_A)
    tasks_b = gen.generate_family_b(tasks_a, SEED_B)
    protocol = PilotProtocol()
    protocol.mark_interaction_complete()
    tasks_c = protocol.generate_family_c(seed=SEED_C, tier=2)
    cfg = PilotConfig()
    all_tasks = {t.task_id: t for t in tasks_a + tasks_b + tasks_c}

    clients, sinks, results = {}, {}, {}
    for arm_name, runner_fn in (
            ("S", arms.run_arm_s), ("S_PRIME", arms.run_arm_sprime),
            ("C", arms.run_arm_c)):
        responder = _naive_responder()
        responder.programs = {tid: t.naive_program for tid, t in
                              all_tasks.items()}
        clients[arm_name] = MockClient(responder)
        sinks[arm_name] = MemorySink()
        results[arm_name] = runner_fn(
            clients[arm_name], cfg, sinks[arm_name], tasks_a, tasks_b,
            tasks_c)
    return tasks_a, tasks_b, tasks_c, clients, sinks, results


class TestPhase0PromptIdentity(unittest.TestCase):
    """Refinement 1: one shared Phase-0 baseline prompt path."""

    def test_baseline_prompt_bytes_identical_across_arms(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        expected = arms.build_baseline_prompt(tasks_a)
        _, _, _, clients, sinks, results = _run_three_arms()
        seen_user = {}
        seen_system = {}
        seen_hash = {}
        for arm_name in ("S", "S_PRIME", "C"):
            baseline_calls = [c for c in clients[arm_name].calls
                              if c["label"].endswith(":baseline:baseline")]
            self.assertEqual(len(baseline_calls), 1, arm_name)
            call = baseline_calls[0]
            self.assertEqual(len(call["messages"]), 1, arm_name)
            self.assertEqual(call["messages"][0]["role"], "user", arm_name)
            seen_user[arm_name] = call["messages"][0]["content"]
            seen_system[arm_name] = call["system"]
            seen_hash[arm_name] = results[arm_name]["phase_0_prompt_sha256"]
        # participant-visible bytes identical across arms
        self.assertEqual(seen_user["S"], seen_user["S_PRIME"])
        self.assertEqual(seen_user["S"], seen_user["C"])
        self.assertEqual(seen_user["S"], expected)
        self.assertEqual(seen_system["S"], seen_system["S_PRIME"])
        self.assertEqual(seen_system["S"], seen_system["C"])
        self.assertEqual(
            seen_hash["S"], hashlib.sha256(expected.encode()).hexdigest())
        self.assertEqual(len(set(seen_hash.values())), 1)
        # and the evidence sink stored the same prompt text per arm
        for arm_name in ("S", "S_PRIME", "C"):
            stored = [text for (arm, phase, _), text
                      in sinks[arm_name].prompts.items()
                      if arm == arm_name and phase == "baseline"]
            self.assertEqual(stored, [expected], arm_name)

    def test_baseline_tasks_identical_across_arms(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        _, _, _, clients, _, _ = _run_three_arms()
        bodies = {}
        for arm_name in ("S", "S_PRIME", "C"):
            call = [c for c in clients[arm_name].calls
                    if c["label"].endswith(":baseline:baseline")][0]
            sections = _task_sections(call["messages"][0]["content"])
            bodies[arm_name] = {
                tid: "\n".join(v) for tid, v in sections.items()}
            self.assertEqual(sorted(sections.keys()),
                             [t.task_id for t in tasks_a], arm_name)
        self.assertEqual(bodies["S"], bodies["S_PRIME"])
        self.assertEqual(bodies["S"], bodies["C"])

    def test_baseline_outputs_independently_generated(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        tasks_b = gen.generate_family_b(tasks_a, SEED_B)
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        tasks_c = protocol.generate_family_c(seed=SEED_C, tier=2)
        cfg = PilotConfig()
        all_tasks = tasks_a + tasks_b + tasks_c

        clients, sinks, results = {}, {}, {}
        for arm_name, runner_fn in (
                ("S", arms.run_arm_s), ("S_PRIME", arms.run_arm_sprime),
                ("C", arms.run_arm_c)):
            def responder(label, call_index, tasks=all_tasks):
                # every call's answer embeds the call label, so answers can
                # never be silently shared between arms
                return "\n".join(
                    _program_section(t.task_id, f"# {label}")
                    for t in tasks)
            clients[arm_name] = MockClient(responder)
            sinks[arm_name] = MemorySink()
            results[arm_name] = runner_fn(
                clients[arm_name], cfg, sinks[arm_name], tasks_a, tasks_b,
                tasks_c)

        baseline_programs = {}
        for arm_name in ("S", "S_PRIME", "C"):
            baseline_programs[arm_name] = {
                tid: entry["program"]
                for tid, entry in
                results[arm_name]["phase_0"]["tasks"].items()}
        # every arm made its OWN baseline call: recorded programs differ
        self.assertNotEqual(baseline_programs["S"],
                            baseline_programs["S_PRIME"])
        self.assertNotEqual(baseline_programs["S"], baseline_programs["C"])
        self.assertNotEqual(baseline_programs["S_PRIME"],
                            baseline_programs["C"])
        # and each arm made exactly one baseline call
        for arm_name in ("S", "S_PRIME", "C"):
            n_baseline = sum(
                1 for c in clients[arm_name].calls
                if c["label"].endswith(":baseline:baseline"))
            self.assertEqual(n_baseline, 1, arm_name)

    def test_no_treatment_labels_in_phase0(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        prompt = arms.build_baseline_prompt(tasks_a).lower()
        system = arms.build_system_prompt(om.PARTICIPANT_SPEC).lower()
        for bad in arms.TREATMENT_LABEL_SUBSTRINGS:
            self.assertNotIn(bad, prompt)
            self.assertNotIn(bad, system)
        # the shared heading itself must be treatment-free
        self.assertNotIn("arm", arms.BASELINE_HEADING.lower())
        # and no baseline prompt saved by any arm contains a label
        _, _, _, _, sinks, _ = _run_three_arms()
        for arm_name, sink in sinks.items():
            for (arm, phase, _), text in sink.prompts.items():
                if arm == arm_name and phase == "baseline":
                    lowered = text.lower()
                    for bad in arms.TREATMENT_LABEL_SUBSTRINGS:
                        self.assertNotIn(bad, lowered)

    def test_baseline_phase_contains_no_feedback_text(self):
        _, _, _, clients, _, _ = _run_three_arms()
        for arm_name in ("S", "S_PRIME", "C"):
            call = [c for c in clients[arm_name].calls
                    if c["label"].endswith(":baseline:baseline")][0]
            text = call["messages"][0]["content"].upper()
            for bad in ("FEEDBACK", "PASS", "FAIL", "ENVIRONMENT",
                        "REVISE"):
                self.assertNotIn(bad, text)


class TestPerInstanceDifficulty(unittest.TestCase):
    """Refinement 2: deterministic per-instance difficulty metadata."""

    def test_difficulty_metadata_recorded_for_every_instance(self):
        for tasks in (gen.generate_family_a(4, SEED_A),
                      gen.generate_family_b(
                          gen.generate_family_a(4, SEED_A), SEED_B)):
            for t in tasks:
                d = t.difficulty
                self.assertIn("stratum_key", d, t.task_id)
                self.assertIn("features", d, t.task_id)
                self.assertIn("naive_discrimination", d, t.task_id)
                feats = d["features"]
                for key in ("recipe", "novel_ops", "multi_statement",
                            "starts_with_out", "uses_queue_ops",
                            "nested_novel_expression", "purity_trap",
                            "arith_op_count", "params", "phrasing"):
                    self.assertIn(key, feats, t.task_id)
                self.assertGreaterEqual(
                    d["naive_discrimination"]["public_fails"], 1)
                self.assertGreaterEqual(
                    d["naive_discrimination"]["hidden_fails"], 2)
                # never participant-facing
                view_text = json.dumps(t.public_view())
                self.assertNotIn("stratum_key", view_text)
                self.assertNotIn("naive_discrimination", view_text)

    def test_same_seed_reproduces_same_difficulty_properties(self):
        t1 = gen.generate_family_a(4, SEED_A)
        t2 = gen.generate_family_a(4, SEED_A)
        self.assertEqual(
            [t.difficulty for t in t1], [t.difficulty for t in t2])
        self.assertEqual([t.difficulty["stratum_key"] for t in t1],
                         [t.difficulty["stratum_key"] for t in t2])
        self.assertEqual(gen.tasks_checksum(t1), gen.tasks_checksum(t2))

    def test_spec_pins_strata_deterministically(self):
        spec = {"swizzle_mul": {"k": 5}, "mirror_add": {"k": 7},
                "swizzle_mul_add": {"k": 4, "m": 3},
                "splice_drain": {"mode": "discard_front"}}
        t1 = gen.generate_family_a(4, SEED_A, spec=spec)
        t2 = gen.generate_family_a(4, SEED_A, spec=spec)
        self.assertEqual([t.difficulty["stratum_key"] for t in t1],
                         [t.difficulty["stratum_key"] for t in t2])
        for t in t1:
            for k, v in spec[t.recipe].items():
                self.assertEqual(t.params[k], v)

    def test_calibration_seeds_and_official_seeds_disjoint(self):
        cfg = PilotConfig()
        official = list(cfg.official_seeds().values())
        cal_namespace = set(range(cfg.seed_calibration_base,
                                  cfg.seed_calibration_max + 1))
        for s in official:
            self.assertNotIn(s, cal_namespace)
        cvi0 = list(cfg.cvi0_seeds().values())
        self.assertFalse(set(official) & set(cvi0))
        # generated instances are disjoint too
        cal_tasks = gen.generate_stratified_calibration_batch(
            calibration.BASELINE_CATALOG, SEED_CAL)
        official_tasks = gen.generate_family_a(4, SEED_A)
        self.assertFalse({t.checksum() for t in cal_tasks}
                         & {t.checksum() for t in official_tasks})
        self.assertFalse({t.seed for t in cal_tasks}
                         & {t.seed for t in official_tasks})

    def test_transfer_calibration_seeds_and_official_b_seeds_disjoint(self):
        cfg = PilotConfig()
        spec = {"swizzle_mul": {"k": 3}, "mirror_add": {"k": 4},
                "swizzle_mul_add": {"k": 2, "m": 1},
                "splice_drain": {"mode": "drain"}}
        cal_a = gen.generate_family_a(4, SEED_CAL, spec=spec,
                                      id_prefix="CAL-A")
        cal_b = gen.generate_family_b(
            cal_a, SEED_CAL + 1, spec=spec,
            s3_spec=calibration.TRANSFER_S3_LEVELS[0])
        off_a = gen.generate_family_a(4, SEED_A, spec=spec)
        off_b = gen.generate_family_b(
            off_a, SEED_B, spec=spec,
            s3_spec=calibration.TRANSFER_S3_LEVELS[0])
        self.assertFalse({t.checksum() for t in cal_b}
                         & {t.checksum() for t in off_b})
        self.assertFalse({t.seed for t in cal_b} & {t.seed for t in off_b})
        self.assertFalse({t.seed for t in cal_a} & {t.seed for t in off_a})
        # seed namespaces asserted numerically as well
        official = cfg.seed_family_b
        for t in cal_b:
            self.assertNotEqual(official, t.seed)

    def test_calibration_batch_instances_are_stratified(self):
        tasks = gen.generate_stratified_calibration_batch(
            calibration.BASELINE_CATALOG, SEED_CAL)
        # one instance per (recipe, stratum) entry of the catalog
        expected = sum(len(v) for v in
                       calibration.BASELINE_CATALOG.values())
        self.assertEqual(len(tasks), expected)
        ids = [t.task_id for t in tasks]
        self.assertEqual(len(ids), len(set(ids)),
                         "calibration task ids must be unique")
        for t in tasks:
            self.assertIn(t.recipe, calibration.BASELINE_CATALOG)
            self.assertEqual(t.family, "CAL")
        strata = [t.difficulty["stratum_key"] for t in tasks]
        self.assertEqual(len(strata), len(set(strata)))


class TestSelectionRules(unittest.TestCase):
    """The selection rules are fixed in code and deterministic."""

    def _key(self, recipe, stratum):
        return calibration._stratum_key(recipe, stratum)

    def test_baseline_rule_selects_first_in_band_family(self):
        instances = []
        # swizzle strata: k=2 -> 0.9, k=3 -> 0.6, k=5 -> 0.4
        # every other stratum: 0.5.  The FIRST spec (fixed enumeration
        # order) has predicted family S0 = (0.9+0.5+0.5+0.5)/4 = 0.6,
        # in band -> accepted; swizzle k=2 is flagged (0.9 > 0.8).
        scores = {
            self._key("swizzle_mul", {"k": 2}): [0.9, 0.9],
            self._key("swizzle_mul", {"k": 3}): [0.6, 0.6],
            self._key("swizzle_mul", {"k": 5}): [0.4, 0.4],
            self._key("mirror_add", {"k": 2}): [0.5, 0.5],
            self._key("mirror_add", {"k": 4}): [0.5, 0.5],
            self._key("mirror_add", {"k": 7}): [0.5, 0.5],
            self._key("swizzle_mul_add", {"k": 2, "m": 1}): [0.5, 0.5],
            self._key("swizzle_mul_add", {"k": 3, "m": 2}): [0.5, 0.5],
            self._key("swizzle_mul_add", {"k": 4, "m": 3}): [0.5, 0.5],
            self._key("splice_drain", {"mode": "drain"}): [0.5, 0.5],
            self._key("splice_drain",
                      {"mode": "discard_front"}): [0.5, 0.5]}
        for key, values in scores.items():
            for v in values:
                instances.append({"stratum_key": key, "score": v})
        sel = calibration.select_baseline_spec({"instances": instances})
        self.assertEqual(sel["status"], "accepted")
        self.assertEqual(sel["spec"]["swizzle_mul"], {"k": 2})
        self.assertAlmostEqual(sel["predicted_s0"], 0.6)
        self.assertIn("swizzle_mul", sel["flagged_strata"])
        # determinism: the rule is a pure function of the records
        sel2 = calibration.select_baseline_spec({"instances": instances})
        self.assertEqual(sel["spec"], sel2["spec"])

    def test_baseline_rule_accepts_recipe_degenerate_family(self):
        # the CVI-0.1 calibration pattern: mirror_add 0.0 everywhere,
        # every other recipe 1.0 everywhere -> predicted family S0 0.75
        # (in band); the degenerate strata are flagged, not rejected.
        instances = []
        for stratum in calibration.BASELINE_CATALOG["mirror_add"]:
            for _ in range(2):
                instances.append(
                    {"stratum_key": self._key("mirror_add", stratum),
                     "score": 0.0})
        for recipe, strata in calibration.BASELINE_CATALOG.items():
            if recipe == "mirror_add":
                continue
            for stratum in strata:
                for _ in range(2):
                    instances.append(
                        {"stratum_key": self._key(recipe, stratum),
                         "score": 1.0})
        sel = calibration.select_baseline_spec({"instances": instances})
        self.assertEqual(sel["status"], "accepted")
        self.assertAlmostEqual(sel["predicted_s0"], 0.75)
        self.assertIn("mirror_add", sel["flagged_strata"])
        self.assertIn("swizzle_mul", sel["flagged_strata"])
        self.assertEqual(sel["flagged_strata"]["mirror_add"]
                         ["stratum_mean"], 0.0)

    def test_baseline_rule_fallback_when_nothing_in_band(self):
        instances = []
        for recipe, stratum in (
                ("swizzle_mul", {"k": 2}), ("mirror_add", {"k": 2}),
                ("swizzle_mul_add", {"k": 2, "m": 1}),
                ("splice_drain", {"mode": "drain"})):
            for _ in range(2):
                instances.append(
                    {"stratum_key": self._key(recipe, stratum),
                     "score": 0.95})
        sel = calibration.select_baseline_spec({"instances": instances})
        self.assertEqual(sel["status"], "fallback")
        self.assertGreater(sel["predicted_s0"], calibration.BAND[1])
        self.assertTrue(sel["reason"])

    def test_transfer_rule_rejects_saturated_level(self):
        attempts = [{
            "level": 0,
            "level_spec": calibration.TRANSFER_S3_LEVELS[0],
            "s_tr_batches": [1.0, 1.0], "s3_batches": [1.0, 1.0],
            "s_tr_mean": 1.0, "s3_mean": 1.0,
        }]
        sel = calibration.select_transfer_level(attempts)
        self.assertEqual(sel["status"], "needs_refinement")
        self.assertEqual(attempts[0]["decision"], "rejected")

    def test_transfer_rule_accepts_in_band_below_ceiling(self):
        attempts = [{
            "level": 0,
            "level_spec": calibration.TRANSFER_S3_LEVELS[0],
            "s_tr_batches": [0.6, 0.7], "s3_batches": [0.4, 0.5],
            "s_tr_mean": 0.65, "s3_mean": 0.45,
        }]
        sel = calibration.select_transfer_level(attempts)
        self.assertEqual(sel["status"], "accepted")
        self.assertEqual(sel["s3_spec"], calibration.TRANSFER_S3_LEVELS[0])


class TestTransferFamilyIntegrity(unittest.TestCase):
    """Refinement 3: Family B harder S3, identical instances across arms."""

    def test_s3_recipes_are_new_compositions(self):
        a = gen.generate_family_a(4, SEED_A)
        b = gen.generate_family_b(a, SEED_B)
        for t in b:
            if t.subfamily == "s3":
                self.assertIn(t.recipe,
                              gen.FAMILY_B_S3_RECIPES)
                # both S3 recipes use operators not used in Family A
                a_ops = {op for ta in a
                         for op in gen.RECIPES[ta.recipe].novel_ops}
                for op in gen.RECIPES[t.recipe].novel_ops:
                    self.assertNotIn(op, a_ops)

    def test_family_b_official_instances_identical_across_arms(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        tasks_b = gen.generate_family_b(tasks_a, SEED_B)
        _, _, _, clients, _, _ = _run_three_arms()
        transfer_texts = {}
        for arm_name in ("S", "S_PRIME", "C"):
            call = [c for c in clients[arm_name].calls
                    if c["label"].endswith(":transfer:transfer")][0]
            transfer_texts[arm_name] = call["messages"][0]["content"]
        self.assertEqual(transfer_texts["S"], transfer_texts["S_PRIME"])
        self.assertEqual(transfer_texts["S"], transfer_texts["C"])
        # every official B instance appears in the shared transfer prompt
        for t in tasks_b:
            for text in transfer_texts.values():
                self.assertIn(f"## Task {t.task_id}", text)
                self.assertIn(t.description, text)

    def test_family_c_gate_and_strata(self):
        protocol = PilotProtocol()
        with self.assertRaises(ProtocolError):
            protocol.generate_family_c(seed=SEED_C, tier=2,
                                       spec={"swizzle_mul": {"k": 3}})
        protocol.mark_interaction_complete()
        spec = {"swizzle_mul": {"k": 3}}
        tasks = protocol.generate_family_c(seed=SEED_C, tier=2, spec=spec)
        for t in tasks:
            if t.recipe in spec:
                for k, v in spec[t.recipe].items():
                    self.assertEqual(t.params[k], v)


if __name__ == "__main__":
    unittest.main()
