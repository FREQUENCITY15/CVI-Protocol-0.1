"""Metrics computations: G_F, retention ratio, gaming index, undefined
handling."""

import json
import unittest

from cvi_lab import metrics

TASKS_A = ["A-01", "A-02", "A-03", "A-04"]
TASKS_C = ["C-01", "C-02", "C-03", "C-04"]
TASKS_B_SUB = {"s1": ["B-S1-01", "B-S1-02"],
               "s2": ["B-S2-01", "B-S2-02"],
               "s3": ["B-S3-01", "B-S3-02"]}
ALL_B = [t for sub in TASKS_B_SUB.values() for t in sub]


def _phase(tasks, scores):
    return {"tasks": {t: {"hidden_score": s} for t, s in scores.items()}}


def _base_result(s0, s_ret, s_tr, s_ver):
    return {
        "phase_0": _phase(TASKS_A, {t: s0 for t in TASKS_A}),
        "phase_a": {"note": "no Phase-1 rounds in this fixture"},
        "phase_post": None,
        "phase_ret": _phase(TASKS_A, {t: s_ret for t in TASKS_A}),
        "phase_transfer": _phase(ALL_B, {t: s_tr for t in ALL_B}),
        "phase_hidden": _phase(TASKS_C, {t: s_ver for t in TASKS_C}),
        "sessions": [],
        "self_report": {"answer": "no answer"},
    }


class TestArmMetrics(unittest.TestCase):
    def test_arm_s_basics(self):
        result = _base_result(0.5, 0.5, 0.25, 0.5)
        m = metrics.compute_arm_metrics("S", result, TASKS_A, TASKS_B_SUB,
                                        TASKS_C)
        self.assertEqual(m["S0"], 0.5)
        self.assertIsNone(m["S_post"])          # no interaction in Arm S
        self.assertEqual(m["S_ret"], 0.5)
        self.assertEqual(m["S_tr"], 0.25)
        self.assertEqual(m["S_ver"], 0.5)
        self.assertIsNone(m["retention_ratio_M"])  # undefined without S_post
        self.assertIsNone(m["gaming_index"])       # C-only
        self.assertEqual(m["revision_rounds_used"], 0)
        for t in TASKS_A:
            self.assertIsNone(m["per_task"][t]["G_F"])  # undefined
            self.assertEqual(m["per_task"][t]["F_before"], 0.5)
            self.assertIsNone(m["per_task"][t]["F_after"])

    def test_arm_sprime_gf_and_retention(self):
        result = _base_result(0.5, 0.5, 0.5, 0.5)
        initial = {t: 0.25 for t in TASKS_A}
        final = {t: 1.0 for t in TASKS_A}
        result["phase_a"] = {
            "revision_rounds_used": 3,
            "rounds": [
                {"round": 0, "programs": {
                    t: {"hidden_score": initial[t]} for t in TASKS_A}},
                {"round": 3, "programs": {
                    t: {"hidden_score": final[t]} for t in TASKS_A}},
            ],
        }
        m = metrics.compute_arm_metrics("S_PRIME", result, TASKS_A,
                                        TASKS_B_SUB, TASKS_C)
        # S0 comes from the shared Phase-0 baseline (0.5), NOT the
        # critique round 0; F_before comes from the Phase-1 initial round.
        self.assertEqual(m["S0"], 0.5)
        self.assertEqual(m["S_post"], 1.0)
        # F_before = 0.75 -> F_after = 0 -> G_F = 1.0 per task
        for t in TASKS_A:
            self.assertAlmostEqual(m["per_task"][t]["G_F"], 1.0)
        self.assertAlmostEqual(m["G_F_mean"], 1.0)
        # M = 1 - (S0 - S_ret)/(S0 - F_after) = 1 - (0.5-0.5)/(0.5-0) = 1.0
        self.assertAlmostEqual(m["retention_ratio_M"], 1.0)

    def test_gf_undefined_when_no_failure(self):
        result = _base_result(1.0, 1.0, 1.0, 1.0)
        initial = {t: 1.0 for t in TASKS_A}
        final = {t: 1.0 for t in TASKS_A}
        result["phase_a"] = {
            "revision_rounds_used": 0,
            "rounds": [
                {"round": 0, "programs": {
                    t: {"hidden_score": initial[t]} for t in TASKS_A}},
                {"round": 1, "programs": {
                    t: {"hidden_score": final[t]} for t in TASKS_A}},
            ],
        }
        m = metrics.compute_arm_metrics("S_PRIME", result, TASKS_A,
                                        TASKS_B_SUB, TASKS_C)
        self.assertIsNone(m["G_F_mean"])
        for t in TASKS_A:
            self.assertIsNone(m["per_task"][t]["G_F"])

    def test_gaming_index(self):
        result = _base_result(0.5, 0.5, 0.5, 0.5)
        rounds = []
        tasks = {}
        for i, t in enumerate(TASKS_A):
            gaming = (i % 2 == 0)  # tasks 0,2 pass public, fail hidden
            tasks[t] = {
                "hidden_score": 0.5 if gaming else 1.0,
                "public_all_pass": True,
                "public_results": [],
                "hidden_results": [],
            }
        rounds.append({"round": 0, "tasks": tasks})
        rounds.append({"round": 1, "tasks": tasks})
        result["phase_a"] = {"rounds": rounds, "final": tasks,
                             "revision_rounds_used": 1}
        m = metrics.compute_arm_metrics("C", result, TASKS_A, TASKS_B_SUB,
                                        TASKS_C)
        self.assertEqual(m["gaming_index"]["rate"], 0.5)
        self.assertEqual(sorted(m["gaming_index"]["gaming_tasks"]),
                         ["A-01", "A-03"])

    def test_undefined_serializes_as_null(self):
        result = _base_result(0.5, 0.5, 0.5, 0.5)
        m = metrics.compute_arm_metrics("S", result, TASKS_A, TASKS_B_SUB,
                                        TASKS_C)
        text = json.dumps(m)
        self.assertIn("null", text)
        d = json.loads(text)
        self.assertIsNone(d["S_post"])

    def test_transfer_by_subfamily(self):
        result = _base_result(0.5, 0.5, 0.5, 0.5)
        tr = result["phase_transfer"]
        tr["tasks"]["B-S3-01"] = {"hidden_score": 1.0}
        tr["tasks"]["B-S3-02"] = {"hidden_score": 1.0}
        m = metrics.compute_arm_metrics("S", result, TASKS_A, TASKS_B_SUB,
                                        TASKS_C)
        self.assertEqual(m["S_tr_by_subfamily"]["s3"], 1.0)
        self.assertEqual(m["S_tr_by_subfamily"]["s1"], 0.5)


class TestFailureEvents(unittest.TestCase):
    def test_events_recorded(self):
        result = _base_result(0.5, 0.5, 0.5, 0.5)
        rounds = [{
            "round": 0,
            "tasks": {
                "A-01": {
                    "public_results": [
                        {"case_id": 1, "passed": False,
                         "error_class": "UNDERFLOW"},
                        {"case_id": 2, "passed": True, "error_class": None}],
                    "hidden_results": [
                        {"case_id": 9, "passed": False,
                         "error_class": None}],
                    "hidden_score": 0.5, "public_all_pass": False,
                }}}]
        result["phase_a"] = {"rounds": rounds, "final": rounds[-1]["tasks"],
                             "revision_rounds_used": 0}
        events = metrics.failure_events(
            {**result, "arm_kind": "C"})
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {(e["visibility"], e["case_id"]) for e in events},
            {("public", 1), ("hidden", 9)})


if __name__ == "__main__":
    unittest.main()
