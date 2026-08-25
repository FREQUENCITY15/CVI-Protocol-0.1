"""OrderMachine VM semantics, determinism, versioning, spec-sheet tests."""

import unittest

from cvi_lab import ordermachine as om


def run(program, registers=None, queue=None, max_steps=None):
    inputs = {"registers": registers or {}, "queue": queue or []}
    return om.OrderMachine().run(program, inputs, max_steps=max_steps)


class TestBasicInstructions(unittest.TestCase):
    def test_set_add_sub_mul_div_out(self):
        r = run("SET a 5\nADD a 3\nSUB a 2\nMUL a 4\nOUT a")
        self.assertIsNone(r.error)
        self.assertEqual(r.output, [24])
        self.assertEqual(r.final_registers["a"], 24)

    def test_div_floor(self):
        r = run("DIV a 2", registers={"a": 7})
        self.assertEqual(r.output, [])
        self.assertEqual(r.final_registers["a"], 3)

    def test_div_zero(self):
        r = run("DIV a 0", registers={"a": 7})
        self.assertEqual(r.error.error_class, om.ERR_DIVZERO)

    def test_queue_push_pop_drain(self):
        r = run("PUSH 1\nPUSH 2\nPUSH 3\nPOP a\nDRAIN", registers={"a": 99})
        self.assertIsNone(r.error)
        self.assertEqual(r.final_registers["a"], 1)
        self.assertEqual(r.output, [2, 3])

    def test_pop_empty(self):
        r = run("POP a")
        self.assertEqual(r.error.error_class, om.ERR_QEMPTY)

    def test_push_full(self):
        program = "\n".join("PUSH 1" for _ in range(65))
        r = run(program)
        self.assertEqual(r.error.error_class, om.ERR_QFULL)

    def test_initial_queue(self):
        r = run("DRAIN", queue=[7, 8])
        self.assertEqual(r.output, [7, 8])

    def test_comments_and_blank_lines(self):
        r = run("# hello\n\nSET a 3   # trailing\nOUT a\n")
        self.assertEqual(r.output, [3])


class TestNovelOperators(unittest.TestCase):
    def test_swizzle(self):
        r = run("SWIZZLE a b", registers={"a": 1, "b": 9})
        self.assertIsNone(r.error)
        self.assertEqual(r.final_registers["a"], 8)
        self.assertEqual(r.final_registers["b"], 9)

    def test_swizzle_underflow(self):
        r = run("SWIZZLE a b", registers={"b": 0})
        self.assertEqual(r.error.error_class, om.ERR_UNDERFLOW)

    def test_mirror(self):
        r = run("OUT MIRROR a", registers={"a": 1})
        self.assertEqual(r.output, [129])  # bitrev(1)+1

    def test_mirror_overflow(self):
        r = run("OUT MIRROR a", registers={"a": 255})
        self.assertEqual(r.error.error_class, om.ERR_OVERFLOW)

    def test_splice_pushes_queue(self):
        r = run("SPLICE a b\nDRAIN", registers={"a": 12, "b": 34})
        self.assertIsNone(r.error)
        self.assertEqual(r.output, [1, 3, 4])

    def test_splice_yields_three(self):
        r = run("OUT SPLICE a b", registers={"a": 12, "b": 34})
        self.assertEqual(r.output, [3])

    def test_helix(self):
        r = run("OUT HELIX a", registers={"a": 1})
        self.assertEqual(r.output, [4])  # rotl(1)+2

    def test_helix_wraps(self):
        r = run("OUT HELIX a", registers={"a": 128})
        self.assertEqual(r.output, [3])  # rotl(128)=1, +2

    def test_fold(self):
        r = run("OUT FOLD a", registers={"a": 34})
        self.assertEqual(r.output, [7])

    def test_nudge(self):
        r = run("OUT NUDGE a", registers={"a": 7})
        self.assertEqual(r.output, [10])

    def test_nudge_overflow(self):
        r = run("OUT NUDGE a", registers={"a": 255})
        self.assertEqual(r.error.error_class, om.ERR_OVERFLOW)


class TestPrecedenceQuirks(unittest.TestCase):
    def test_novel_op_capture(self):
        # SWIZZLE a b * 2  ==  SWIZZLE(a, b*2)  -> a := b*2 - 1
        r = run("OUT SWIZZLE a b * 2", registers={"a": 0, "b": 7})
        self.assertEqual(r.output, [13])
        self.assertEqual(r.final_registers["a"], 13)

    def test_parenthesised_novel_op(self):
        # (SWIZZLE a b) * 2  ->  a := b-1, output (b-1)*2
        r = run("OUT (SWIZZLE a b) * 2", registers={"a": 0, "b": 7})
        self.assertEqual(r.output, [12])
        self.assertEqual(r.final_registers["a"], 6)

    def test_mirror_capture(self):
        r = run("OUT MIRROR a + 3", registers={"a": 0})
        # MIRROR(a + 3) = bitrev(3)+1 = 192+1 = 193
        self.assertEqual(r.output, [193])

    def test_mirror_parenthesised(self):
        r = run("OUT (MIRROR a) + 3", registers={"a": 0})
        # bitrev(0)+1+3 = 0+1+3 = 4
        self.assertEqual(r.output, [4])

    def test_novel_op_mid_expression_is_syntax_error(self):
        r = run("OUT 1 + SWIZZLE a b", registers={"a": 0, "b": 3})
        self.assertIsNotNone(r.error)
        self.assertEqual(r.error.error_class, om.ERR_SYNTAX)

    def test_bare_novel_statement_side_effect(self):
        r = run("SWIZZLE a b\nOUT a", registers={"a": 0, "b": 5})
        self.assertEqual(r.output, [4])

    def test_binary_novel_first_operand_atom(self):
        # first operand of a binary novel op must be a register/literal/(...)
        r = run("OUT SWIZZLE a + 1 b", registers={"a": 0, "b": 3})
        self.assertEqual(r.error.error_class, om.ERR_SYNTAX)


class TestErrorsAndLimits(unittest.TestCase):
    def test_underflow(self):
        r = run("SUB a 1", registers={"a": 0})
        self.assertEqual(r.error.error_class, om.ERR_UNDERFLOW)

    def test_overflow(self):
        r = run("ADD a 255", registers={"a": 1})
        self.assertEqual(r.error.error_class, om.ERR_OVERFLOW)

    def test_bad_literal(self):
        r = run("SET a 256")
        self.assertEqual(r.error.error_class, om.ERR_BAD_LITERAL)

    def test_undef_register_input(self):
        r = run("OUT a", registers={"g": 1})
        self.assertEqual(r.error.error_class, om.ERR_UNDEF_REGISTER)

    def test_unknown_register_in_program_is_syntax_error(self):
        r = run("SET g 1")
        self.assertEqual(r.error.error_class, om.ERR_SYNTAX)

    def test_step_limit(self):
        program = "\n".join("SET a 1" for _ in range(11))
        r = run(program, max_steps=10)
        self.assertEqual(r.error.error_class, om.ERR_STEP_LIMIT)

    def test_trailing_tokens_one_instruction_per_line(self):
        r = run("SET a 1 OUT a")
        self.assertEqual(r.error.error_class, om.ERR_SYNTAX)


class TestDeterminismAndIsolation(unittest.TestCase):
    def test_deterministic_repeat(self):
        program = "SWIZZLE a b\nSPLICE a b\nDRAIN\nOUT a"
        inputs = {"registers": {"a": 4, "b": 17}, "queue": [9]}
        vm = om.OrderMachine()
        r1 = vm.run(program, inputs)
        r2 = vm.run(program, inputs)
        self.assertEqual(r1.output, r2.output)
        self.assertEqual(r1.final_registers, r2.final_registers)
        self.assertEqual(r1.steps, r2.steps)

    def test_fresh_state_per_run(self):
        vm = om.OrderMachine()
        vm.run("SET a 200", {"registers": {}, "queue": []})
        r = vm.run("OUT a", {"registers": {}, "queue": []})
        self.assertEqual(r.output, [0])  # state did not persist

    def test_error_is_deterministic(self):
        program = "SWIZZLE a b"
        inputs = {"registers": {"b": 0}, "queue": []}
        e1 = om.OrderMachine().run(program, inputs).error
        e2 = om.OrderMachine().run(program, inputs).error
        self.assertEqual(e1.error_class, e2.error_class)
        self.assertEqual(e1.to_dict(), e2.to_dict())


class TestVersionedSubmissions(unittest.TestCase):
    def test_versioning(self):
        log = om.SubmissionLog("T")
        r1 = log.submit("SET a 1")
        r2 = log.submit("SET a 2")
        self.assertEqual((r1.version, r2.version), (1, 2))
        self.assertNotEqual(r1.submission_id, r2.submission_id)
        entries = log.entries()
        entries.clear()  # caller cannot mutate the log through the copy
        self.assertEqual(len(log.entries()), 2)


class TestSpecSheet(unittest.TestCase):
    def test_spec_covers_language(self):
        spec = om.PARTICIPANT_SPEC
        for op in ("SWIZZLE", "MIRROR", "SPLICE", "HELIX", "FOLD", "NUDGE",
                   "SET", "ADD", "SUB", "MUL", "DIV", "OUT", "PUSH", "POP",
                   "DRAIN"):
            self.assertIn(op, spec)
        for err in ("SYNTAX", "UNDERFLOW", "OVERFLOW", "DIVZERO", "QEMPTY",
                    "QFULL", "STEP_LIMIT", "BAD_LITERAL"):
            self.assertIn(err, spec)

    def test_spec_contains_no_privileged_material(self):
        spec = om.PARTICIPANT_SPEC.lower()
        for forbidden in ("hidden", "seed", "grader", "generator", "answer"):
            self.assertNotIn(forbidden, spec,
                             f"spec sheet must not mention {forbidden!r}")


if __name__ == "__main__":
    unittest.main()
