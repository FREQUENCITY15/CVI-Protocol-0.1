"""Grader determinism and the permitted-feedback contract."""

import json
import unittest

from cvi_lab import generator as gen
from cvi_lab import grader

SEED = 424242


class TestGrader(unittest.TestCase):
    def setUp(self):
        self.tasks = gen.generate_family_a(4, SEED)

    def test_canonical_full_score(self):
        for task in self.tasks:
            self.assertEqual(grader.hidden_score(task,
                                                 task.canonical_program), 1.0)

    def test_naive_partial_score(self):
        for task in self.tasks:
            self.assertLess(grader.hidden_score(task, task.naive_program),
                            1.0)

    def test_determinism(self):
        for task in self.tasks:
            r1 = grader.run_hidden(task, task.naive_program)
            r2 = grader.run_hidden(task, task.naive_program)
            self.assertEqual([x.to_dict() for x in r1],
                             [x.to_dict() for x in r2])

    def test_public_all_pass(self):
        for task in self.tasks:
            r = grader.run_public(task, task.canonical_program)
            self.assertTrue(grader.public_all_pass(r))
            r_naive = grader.run_public(task, task.naive_program)
            self.assertFalse(grader.public_all_pass(r_naive))


class TestFeedbackContract(unittest.TestCase):
    def setUp(self):
        self.tasks = gen.generate_family_a(4, SEED)

    def test_feedback_shapes(self):
        for task in self.tasks:
            results = grader.run_public(task, task.naive_program)
            text = grader.feedback_text(task.task_id, results)
            self.assertIn(task.task_id, text)
            self.assertTrue(any(m in text for m in ("PASS", "FAIL")))

    def test_feedback_never_contains_expected_outputs(self):
        for task in self.tasks:
            results = grader.run_public(task, task.naive_program)
            text = grader.feedback_text(task.task_id, results)
            for case in task.public_cases + task.hidden_cases:
                self.assertNotIn(json.dumps(case.expected_output), text)

    def test_feedback_never_contains_input_values(self):
        for task in self.tasks:
            results = grader.run_public(task, task.naive_program)
            text = grader.feedback_text(task.task_id, results)
            for case in task.public_cases + task.hidden_cases:
                self.assertNotIn(json.dumps(case.inputs), text)

    def test_feedback_reports_error_classes(self):
        # A program that errors must produce an error-class mention.
        task = self.tasks[0]  # swizzle_mul
        program = "SWIZZLE a b"  # underflows when b = 0 in some case
        results = grader.run_public(task, program)
        text = grader.feedback_text(task.task_id, results)
        if any(r.error_class for r in results):
            self.assertIn("error:", text)

    def test_feedback_only_permitted_fields(self):
        # Every FAIL clause must be exactly "case N: FAIL (...)" with either
        # an error class or 'wrong output' — nothing else.
        import re
        for task in self.tasks:
            results = grader.run_public(task, task.naive_program)
            text = grader.feedback_text(task.task_id, results)
            stripped = text.split(":", 1)[1]
            for clause in stripped.split("|"):
                clause = clause.strip()
                if clause.startswith("case "):
                    self.assertRegex(
                        clause,
                        r"^case \d+: (PASS|FAIL \(error: [A-Z_]+\)"
                        r"|FAIL \(wrong output\))$")


if __name__ == "__main__":
    unittest.main()
