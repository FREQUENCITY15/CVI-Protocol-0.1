"""Seeded generator: determinism, validity, public/hidden split,
difficulty knob, Family B structure, Family C independence."""

import json
import unittest

from cvi_lab import generator as gen
from cvi_lab import ordermachine as om
from cvi_lab.grader import hidden_score, run_hidden, run_public

SEED_A = 111111
SEED_B = 222222
SEED_C = 333333


class TestDeterminism(unittest.TestCase):
    def test_same_seed_same_tasks(self):
        t1 = gen.generate_family_a(4, SEED_A)
        t2 = gen.generate_family_a(4, SEED_A)
        self.assertEqual(gen.serialize_tasks(t1), gen.serialize_tasks(t2))
        self.assertEqual(gen.tasks_checksum(t1), gen.tasks_checksum(t2))

    def test_different_seed_different_tasks(self):
        t1 = gen.generate_family_a(4, SEED_A)
        t2 = gen.generate_family_a(4, SEED_A + 1)
        self.assertNotEqual(gen.tasks_checksum(t1), gen.tasks_checksum(t2))

    def test_prng_stable(self):
        r1 = gen.SeededRandom(42)
        r2 = gen.SeededRandom(42)
        self.assertEqual([r1.randint(0, 255) for _ in range(100)],
                         [r2.randint(0, 255) for _ in range(100)])


class TestValidity(unittest.TestCase):
    def test_canonical_passes_everything(self):
        vm = om.OrderMachine()
        for task in gen.generate_family_a(4, SEED_A):
            for case in task.public_cases + task.hidden_cases:
                r = vm.run(task.canonical_program, case.inputs)
                self.assertIsNone(
                    r.error, f"{task.task_id} canonical error: {r.error}")
                self.assertEqual(
                    r.output, case.expected_output,
                    f"{task.task_id} canonical wrong on case {case.case_id}")

    def test_naive_misparse_fails(self):
        vm = om.OrderMachine()
        for task in gen.generate_family_a(4, SEED_A):
            public_fails = sum(
                1 for c in task.public_cases
                if (lambda r: r.error is not None
                    or r.output != c.expected_output)(
                        vm.run(task.naive_program, c.inputs)))
            hidden_fails = sum(
                1 for c in task.hidden_cases
                if (lambda r: r.error is not None
                    or r.output != c.expected_output)(
                        vm.run(task.naive_program, c.inputs)))
            self.assertGreaterEqual(public_fails, 1, task.task_id)
            self.assertGreaterEqual(hidden_fails, 2, task.task_id)

    def test_all_cases_distinct_and_in_range(self):
        for task in gen.generate_family_a(4, SEED_A):
            seen = set()
            for case in task.public_cases + task.hidden_cases:
                key = json.dumps(case.inputs, sort_keys=True)
                self.assertNotIn(key, seen, task.task_id)
                seen.add(key)
                for reg, value in case.inputs["registers"].items():
                    self.assertTrue(0 <= value <= 255, task.task_id)
                for value in case.inputs["queue"]:
                    self.assertTrue(0 <= value <= 255, task.task_id)

    def test_scores_meaningful(self):
        for task in gen.generate_family_a(4, SEED_A):
            self.assertEqual(hidden_score(task, task.canonical_program), 1.0)
            self.assertLess(hidden_score(task, task.naive_program), 1.0)


class TestPublicHiddenSplit(unittest.TestCase):
    def test_counts(self):
        for task in gen.generate_family_a(4, SEED_A):
            self.assertEqual(len(task.public_cases),
                             gen.PUBLIC_CASES_PER_TASK)
            self.assertEqual(len(task.hidden_cases),
                             gen.HIDDEN_CASES_PER_TASK)

    def test_public_view_has_no_hidden_keys(self):
        task = gen.generate_family_a(4, SEED_A)[0]
        view = task.public_view()
        self.assertEqual(set(view.keys()),
                         {"task_id", "description", "public_examples"})
        for bad in ("hidden", "seed", "params", "program"):
            self.assertNotIn(bad, json.dumps(view))

    def test_public_view_string_contains_no_hidden_values(self):
        for task in gen.generate_family_a(4, SEED_A):
            view_text = json.dumps(task.public_view())
            for case in task.hidden_cases:
                # Hidden case input vectors are unique across all cases, so
                # their absence proves no hidden case leaks into the view.
                self.assertNotIn(json.dumps(case.inputs), view_text)
                pair = json.dumps({"inputs": case.inputs,
                                   "expected_output": case.expected_output})
                self.assertNotIn(pair, view_text)

    def test_public_cases_themselves_visible(self):
        # sanity: the public cases ARE in the view (they are permitted)
        task = gen.generate_family_a(4, SEED_A)[0]
        view_text = json.dumps(task.public_view())
        for case in task.public_cases:
            self.assertIn(json.dumps(case.inputs), view_text)


class TestFamilyB(unittest.TestCase):
    def test_structure(self):
        a = gen.generate_family_a(4, SEED_A)
        b = gen.generate_family_b(a, SEED_B)
        subs = [t.subfamily for t in b]
        self.assertEqual(sorted(subs), ["s1", "s1", "s2", "s2", "s3", "s3"])

    def test_s1_reworded_duplicates(self):
        a = gen.generate_family_a(4, SEED_A)
        b = gen.generate_family_b(a, SEED_B)
        s1_swizzle = next(t for t in b if t.subfamily == "s1"
                          and t.recipe == "swizzle_mul")
        a_swizzle = next(t for t in a if t.recipe == "swizzle_mul")
        self.assertEqual(s1_swizzle.params, a_swizzle.params)
        self.assertEqual(
            [c.inputs for c in s1_swizzle.hidden_cases],
            [c.inputs for c in a_swizzle.hidden_cases])
        self.assertNotEqual(s1_swizzle.description, a_swizzle.description)

    def test_s2_new_registers_consistent(self):
        a = gen.generate_family_a(4, SEED_A)
        b = gen.generate_family_b(a, SEED_B)
        s2_swizzle = next(t for t in b if t.subfamily == "s2"
                          and t.recipe == "swizzle_mul")
        self.assertIn("c", s2_swizzle.description)
        self.assertIn("d", s2_swizzle.description)
        for case in s2_swizzle.public_cases + s2_swizzle.hidden_cases:
            self.assertEqual(set(case.inputs["registers"].keys()), {"c", "d"})

    def test_s3_different_novel_operators(self):
        a = gen.generate_family_a(4, SEED_A)
        b = gen.generate_family_b(a, SEED_B)
        s3_recipes = {t.recipe for t in b if t.subfamily == "s3"}
        a_ops = {t.recipe for t in a}
        # CVI-0.1 S3: nested/queue novel compositions, different operators
        # from Family A, same structural pattern.
        self.assertTrue({"fold_helix_add", "helix_push_drain"}
                        .issubset(s3_recipes))
        self.assertFalse({"fold_helix_add", "helix_push_drain"} & a_ops)
        for t in b:
            if t.subfamily == "s3":
                # different surface operators from Family A's recipes
                self.assertNotIn(t.recipe, a_ops)

    def test_s3_canonical_passes(self):
        vm = om.OrderMachine()
        a = gen.generate_family_a(4, SEED_A)
        for task in gen.generate_family_b(a, SEED_B):
            for case in task.public_cases + task.hidden_cases:
                r = vm.run(task.canonical_program, case.inputs)
                self.assertIsNone(r.error, task.task_id)
                self.assertEqual(r.output, case.expected_output)


class TestFamilyC(unittest.TestCase):
    def test_fresh_seed_unseen_draws(self):
        a = gen.generate_family_a(4, SEED_A)
        c = gen.generate_family_c(SEED_C)
        for ca in c:
            for ta in a:
                self.assertNotEqual(
                    ca.hidden_cases, ta.hidden_cases,
                    "Family C must not reuse Family A instances")
        self.assertNotEqual(gen.tasks_checksum(a), gen.tasks_checksum(c))

    def test_family_c_task_ids_distinct(self):
        a = gen.generate_family_a(4, SEED_A)
        c = gen.generate_family_c(SEED_C)
        a_ids = {t.task_id for t in a}
        c_ids = {t.task_id for t in c}
        self.assertTrue(all(tid.startswith("C-") for tid in c_ids))
        self.assertFalse(a_ids & c_ids)

    def test_family_c_valid(self):
        vm = om.OrderMachine()
        for task in gen.generate_family_c(SEED_C):
            for case in task.public_cases + task.hidden_cases:
                r = vm.run(task.canonical_program, case.inputs)
                self.assertIsNone(r.error)
                self.assertEqual(r.output, case.expected_output)


class TestDifficultyKnob(unittest.TestCase):
    def test_tier_changes_parameter_draws(self):
        t1 = gen.generate_family_a(4, SEED_A, tier=1)
        t2 = gen.generate_family_a(4, SEED_A, tier=3)
        # Same seed, different tier -> different parameter draws (k values)
        self.assertNotEqual(
            [t.params.get("k") for t in t1],
            [t.params.get("k") for t in t2])

    def test_tier_preserves_validity(self):
        vm = om.OrderMachine()
        for tier in (1, 2, 3):
            for task in gen.generate_family_a(4, SEED_A, tier=tier):
                for case in task.public_cases + task.hidden_cases:
                    r = vm.run(task.canonical_program, case.inputs)
                    self.assertIsNone(r.error)
                    self.assertEqual(r.output, case.expected_output)


if __name__ == "__main__":
    unittest.main()
