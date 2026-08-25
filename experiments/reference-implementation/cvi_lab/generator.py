"""
Deterministic, seeded, procedural task generation for the CVI pilot.

Families (per the authoritative design, pilot sizes):

* Family A  "repair family"      K=4 tasks: one novel rule each
  (a novel operator + a novelty in how expressions are written), calibrated
  into the 0.30-0.80 baseline band.
* Family B  "transfer family"    small set:
      B-S1  paraphrase controls  (same rule/params/cases as two A tasks,
                                  only the wording changes)
      B-S2  novel-parameter controls (same recipes, new parameters/registers)
      B-S3  novel-composition transfer (DIFFERENT novel operators, same
                                  structural pattern: novel-op-with-twist +
                                  expression quirk)
* Family C  "hidden verification family"  4 tasks from the same generator
  config as A but FRESH seeds and unseen parameter draws.  Generated only
  after all interaction phases have completed (enforced by protocol.py,
  not by this pure generator).

Every task carries:
  * a participant-facing description,
  * public worked examples (inputs -> expected output),
  * hidden grader cases (inputs -> expected output),
  * generator-internal material the participant must never see:
    recipe parameters, the canonical intended program, the "naive misparse"
    program used for validity checks, and the hidden seed.

Validity guarantees (checked mechanically at generation time):
  * the canonical program passes every public AND hidden case,
  * the naive misparse program fails at least 1 public and >= 2 hidden cases
    (so the tasks actually discriminate expression-quirk comprehension),
  * all cases are distinct and in-range.

Randomness: a tiny splitmix64 PRNG (no library RNG, stable across Python
versions and platforms).  Regeneration from the recorded seeds reproduces
the identical instances bit-for-bit.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import ordermachine as om

GENERATOR_VERSION = "1.1.0"

PUBLIC_CASES_PER_TASK = 4
HIDDEN_CASES_PER_TASK = 8
MAX_CASE_ATTEMPTS = 20_000


# ---------------------------------------------------------------------------
# Deterministic PRNG (splitmix64)
# ---------------------------------------------------------------------------

class SeededRandom:
    """Splitmix64-based deterministic PRNG."""

    def __init__(self, seed: int):
        self.state: int = seed & 0xFFFFFFFFFFFFFFFF

    def next64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def randint(self, lo: int, hi: int) -> int:
        """Uniform integer in [lo, hi] (inclusive), rejection-sampled."""
        if lo > hi:
            raise ValueError("empty range")
        span = hi - lo + 1
        limit = (0xFFFFFFFFFFFFFFFF // span) * span
        while True:
            r = self.next64()
            if r < limit:
                return lo + (r % span)


class GeneratorError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Task data model
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    case_id: int
    inputs: Dict[str, Any]          # {"registers": {...}, "queue": [...]}
    expected_output: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    task_id: str
    family: str                     # "A" | "B" | "C"
    subfamily: str                  # "repair" | "s1" | "s2" | "s3" | "hidden"
    recipe: str
    tier: int
    seed: int                       # task generation seed
    case_seed: int                  # seed for case sampling (hidden material)
    description: str                # participant-facing
    public_cases: List[TestCase] = field(default_factory=list)
    hidden_cases: List[TestCase] = field(default_factory=list)
    # -- generator-internal (NEVER participant-facing) --
    params: Dict[str, Any] = field(default_factory=dict)
    canonical_program: str = ""
    naive_program: str = ""
    phrasing: int = 1               # description wording variant
    difficulty: Dict[str, Any] = field(default_factory=dict)
    # per-instance structural difficulty metadata (recorded, not
    # participant-facing); filled by difficulty_profile() at build time

    def checksum(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        d = dict(d)
        d["public_cases"] = [TestCase(**c) for c in d["public_cases"]]
        d["hidden_cases"] = [TestCase(**c) for c in d["hidden_cases"]]
        return cls(**d)

    def public_view(self) -> Dict[str, Any]:
        """The ONLY participant-visible representation of a task.

        Deliberately drops hidden cases, seeds, parameters, and all programs.
        """
        return {
            "task_id": self.task_id,
            "description": self.description,
            "public_examples": [
                {"case_id": c.case_id, "inputs": c.inputs,
                 "expected_output": c.expected_output}
                for c in self.public_cases],
        }


# ---------------------------------------------------------------------------
# Recipes
# ---------------------------------------------------------------------------

class Recipe:
    """A parameterised mapping plus its canonical and naive programs.

    `evaluate` computes the intended output directly (never by running the
    participant's program).  `canonical` is the intended program text.
    `naive` is the plausible misparse of a careless reader (the program
    whose parse the expression quirk silently changes).
    """

    name = ""
    novel_ops = ()
    tier = 2

    def params_for(self, rng: SeededRandom, tier: int) -> Dict[str, Any]:
        raise NotImplementedError

    def evaluate(self, inputs: Dict[str, Any], params: Dict[str, Any]
                 ) -> List[int]:
        raise NotImplementedError

    def canonical(self, params: Dict[str, Any]) -> str:
        raise NotImplementedError

    def naive(self, params: Dict[str, Any]) -> str:
        raise NotImplementedError

    def describe(self, params: Dict[str, Any], phrasing: int = 1) -> str:
        raise NotImplementedError

    def draw_inputs(self, rng: SeededRandom, params: Dict[str, Any]
                    ) -> Optional[Dict[str, Any]]:
        """Draw a random input vector that keeps every reading of the task
        (intended AND naive) in range and error-free.  Return None when the
        draw was rejected."""
        raise NotImplementedError


class SwizzleMulRecipe(Recipe):
    name = "swizzle_mul"
    novel_ops = ("SWIZZLE",)
    tier = 2

    def params_for(self, rng, tier):
        k_choices = {1: (2,), 2: (2, 3), 3: (4, 5)}[tier]
        k = k_choices[rng.randint(0, len(k_choices) - 1)]
        r1 = "a"
        r2 = "b"
        return {"k": k, "r1": r1, "r2": r2}

    def evaluate(self, inputs, params):
        b = inputs["registers"][params["r2"]]
        k = params["k"]
        return [((b - 1) * k)]

    def canonical(self, params):
        return f"OUT (SWIZZLE {params['r1']} {params['r2']}) * {params['k']}"

    def naive(self, params):
        return f"OUT SWIZZLE {params['r1']} {params['r2']} * {params['k']}"

    def describe(self, params, phrasing=1):
        k = params["k"]
        r1, r2 = params["r1"], params["r2"]
        if phrasing == 1:
            return (f"Read registers {r1} and {r2}. Apply SWIZZLE to the "
                    f"pair ({r1}, {r2}). Take the value that SWIZZLE "
                    f"produces and multiply it by {k}. Output the result.")
        return (f"Start from the registers {r1} and {r2}. Use the SWIZZLE "
                f"operator on these two registers. Whatever number the "
                f"operator yields, scale it by a factor of {k}, and emit "
                f"that final number.")

    def draw_inputs(self, rng, params):
        k = params["k"]
        hi_b = (255 + 1) // k  # b*k <= 255 for the naive reading
        hi_b = min(hi_b, 255)
        if hi_b < 1:
            return None
        b = rng.randint(1, hi_b)
        a = rng.randint(0, 255)
        return {"registers": {params["r1"]: a, params["r2"]: b}, "queue": []}


class MirrorAddRecipe(Recipe):
    name = "mirror_add"
    novel_ops = ("MIRROR",)
    tier = 2

    def params_for(self, rng, tier):
        k_choices = {1: (1, 2), 2: (2, 3, 4), 3: (5, 6, 7)}[tier]
        k = k_choices[rng.randint(0, len(k_choices) - 1)]
        return {"k": k, "r1": "a"}

    def evaluate(self, inputs, params):
        a = inputs["registers"][params["r1"]]
        return [om.OrderMachine.bit_reverse(a) + 1 + params["k"]]

    def canonical(self, params):
        return f"OUT (MIRROR {params['r1']}) + {params['k']}"

    def naive(self, params):
        return f"OUT MIRROR {params['r1']} + {params['k']}"

    def describe(self, params, phrasing=1):
        k, r1 = params["k"], params["r1"]
        if phrasing == 1:
            return (f"Read register {r1}. Apply MIRROR to it. Add {k} to "
                    f"the value that MIRROR produces. Output the result.")
        return (f"Consider the single register {r1}. Run the MIRROR "
                f"operation over it, then raise the number it hands back by "
                f"{k}. That increased number is what you should output.")

    def draw_inputs(self, rng, params):
        k, r1 = params["k"], params["r1"]
        candidates = []
        for a in range(0, 255):
            rev = om.OrderMachine.bit_reverse(a)
            if rev + 1 + k <= 255 and a + k <= 255 \
                    and om.OrderMachine.bit_reverse(a + k) + 1 <= 255:
                candidates.append(a)
        if not candidates:
            return None
        a = candidates[rng.randint(0, len(candidates) - 1)]
        return {"registers": {r1: a}, "queue": []}


class SwizzleMulAddRecipe(Recipe):
    name = "swizzle_mul_add"
    novel_ops = ("SWIZZLE",)
    tier = 3

    def params_for(self, rng, tier):
        choices = {1: ((2, 1),), 2: ((2, 1), (3, 2)), 3: ((4, 2), (4, 3))}[tier]
        k, m = choices[rng.randint(0, len(choices) - 1)]
        return {"k": k, "m": m, "r1": "a", "r2": "b"}

    def evaluate(self, inputs, params):
        b = inputs["registers"][params["r2"]]
        return [((b - 1) * params["k"] + params["m"])]

    def canonical(self, params):
        return (f"OUT (SWIZZLE {params['r1']} {params['r2']}) "
                f"* {params['k']} + {params['m']}")

    def naive(self, params):
        return (f"OUT SWIZZLE {params['r1']} {params['r2']} "
                f"* {params['k']} + {params['m']}")

    def describe(self, params, phrasing=1):
        k, m = params["k"], params["m"]
        r1, r2 = params["r1"], params["r2"]
        if phrasing == 1:
            return (f"Read registers {r1} and {r2}. Apply SWIZZLE to the "
                    f"pair ({r1}, {r2}). Multiply the value that SWIZZLE "
                    f"produces by {k}, then add {m}. Output the result.")
        return (f"Take registers {r1} and {r2} as your inputs. SWIZZLE them "
                f"together. The number that comes out is then multiplied by "
                f"{k} and afterwards increased by {m}. Emit the number you "
                f"end up with.")

    def draw_inputs(self, rng, params):
        k, m = params["k"], params["m"]
        hi_b = (255 - m + k) // k
        hi_b = min(hi_b, 255)
        if hi_b < 1:
            return None
        b = rng.randint(1, hi_b)
        a = rng.randint(0, 255)
        return {"registers": {"a": a, "b": b}, "queue": []}


class SpliceDrainRecipe(Recipe):
    name = "splice_drain"
    novel_ops = ("SPLICE",)
    tier = 1

    def params_for(self, rng, tier):
        return {"r1": "a", "r2": "b", "mode": "drain"}

    def evaluate(self, inputs, params):
        a = inputs["registers"][params["r1"]]
        b = inputs["registers"][params["r2"]]
        da = om.OrderMachine.digits(a)
        db = om.OrderMachine.digits(b)
        interleaved = [da[0], db[0], da[1], db[1]]
        surviving = [v for i, v in enumerate(interleaved)
                     if (i + 1) % 3 != 0]
        if params.get("mode") == "discard_front":
            return surviving[1:]
        return surviving

    def canonical(self, params):
        if params.get("mode") == "discard_front":
            return f"SPLICE {params['r1']} {params['r2']}\nPOP c\nDRAIN"
        return f"SPLICE {params['r1']} {params['r2']}\nDRAIN"

    def naive(self, params):
        if params.get("mode") == "discard_front":
            return f"SPLICE {params['r1']} {params['r2']}\nDRAIN"
        return f"OUT SPLICE {params['r1']} {params['r2']}"

    def describe(self, params, phrasing=1):
        r1, r2 = params["r1"], params["r2"]
        if params.get("mode") == "discard_front":
            if phrasing == 1:
                return (f"Read registers {r1} and {r2}. Use SPLICE on the "
                        f"pair ({r1}, {r2}). SPLICE puts three numbers onto "
                        f"the queue. Remove the front element of the queue "
                        f"and throw it away. Move the remaining queue "
                        f"elements to the output, front to back.")
            return (f"The registers {r1} and {r2} hold your data. Run the "
                    f"SPLICE operator over those two registers; doing so "
                    f"loads the queue with three values. Take the oldest "
                    f"queued value and discard it. Then transfer the rest "
                    f"of the queue, oldest first, into the output.")
        if phrasing == 1:
            return (f"Read registers {r1} and {r2}. Use SPLICE on the pair "
                    f"({r1}, {r2}). SPLICE puts three numbers onto the "
                    f"queue. Move the entire queue to the output, front to "
                    f"back.")
        return (f"The registers {r1} and {r2} hold your data. Run the "
                f"SPLICE operator over those two registers; doing so loads "
                f"the queue with three values. Then transfer everything "
                f"currently sitting in the queue, oldest first, into the "
                f"output.")

    def draw_inputs(self, rng, params):
        a = rng.randint(0, 255)
        b = rng.randint(0, 255)
        return {"registers": {"a": a, "b": b}, "queue": []}


class HelixMulAddRecipe(Recipe):
    """Family B S3: different novel operator, same structural pattern
    (unary novel op with a twist + arithmetic around it)."""
    name = "helix_mul_add"
    novel_ops = ("HELIX",)
    tier = 2

    def params_for(self, rng, tier):
        return {"k": 2, "m": 3, "r1": "a"}

    def evaluate(self, inputs, params):
        a = inputs["registers"][params["r1"]]
        rot = om.OrderMachine.rotate_left(a)
        return [((rot + 2) * params["k"] + params["m"])]

    def canonical(self, params):
        return f"OUT (HELIX {params['r1']}) * {params['k']} + {params['m']}"

    def naive(self, params):
        return f"OUT HELIX {params['r1']} * {params['k']} + {params['m']}"

    def describe(self, params, phrasing=1):
        r1 = params["r1"]
        return (f"Read register {r1}. Apply HELIX to it. Multiply the value "
                f"that HELIX produces by {params['k']}, then add "
                f"{params['m']}. Output the result.")

    def draw_inputs(self, rng, params):
        # naive reading needs a*k+m <= 255; intended needs
        # (rotl(a)+2)*k+m <= 255 (HELIX itself wraps, no error).
        k, m = params["k"], params["m"]
        hi_a = (255 - m) // k
        if hi_a < 0:
            return None
        candidates = []
        for a in range(0, min(hi_a, 255) + 1):
            rot = om.OrderMachine.rotate_left(a)
            if (rot + 2) * k + m <= 255:
                candidates.append(a)
        if not candidates:
            return None
        a = candidates[rng.randint(0, len(candidates) - 1)]
        return {"registers": {params["r1"]: a}, "queue": []}


class NudgeAddRecipe(Recipe):
    """Family B S3: different novel operator, same structural pattern."""
    name = "nudge_add"
    novel_ops = ("NUDGE",)
    tier = 2

    def params_for(self, rng, tier):
        k = rng.randint(2, 3)
        return {"k": k, "r1": "b"}

    def evaluate(self, inputs, params):
        b = inputs["registers"][params["r1"]]
        return [b + om.OrderMachine.popcount(b) + params["k"]]

    def canonical(self, params):
        return f"OUT (NUDGE {params['r1']}) + {params['k']}"

    def naive(self, params):
        return f"OUT NUDGE {params['r1']} + {params['k']}"

    def describe(self, params, phrasing=1):
        return (f"Read register {params['r1']}. Apply NUDGE to it. Add "
                f"{params['k']} to the value that NUDGE produces. Output "
                f"the result.")

    def draw_inputs(self, rng, params):
        k = params["k"]
        # naive: b + k + popcount(b+k) <= 255; intended: b+popcount(b)+k<=255
        candidates = []
        for b in range(0, 255 - k + 1):
            if b + om.OrderMachine.popcount(b) + k <= 255 \
                    and b + k + om.OrderMachine.popcount(b + k) <= 255:
                candidates.append(b)
        if not candidates:
            return None
        b = candidates[rng.randint(0, len(candidates) - 1)]
        return {"registers": {params["r1"]: b}, "queue": []}


class FoldHelixAddRecipe(Recipe):
    """Family B S3 (CVI-0.1): nested unary novel composition — HELIX then
    FOLD — with the Family-A expression quirk.  The naive misparse drops
    the parentheses and the '+ k' is swallowed into the innermost operand:
    `FOLD HELIX a + k` means FOLD(HELIX(a + k)), not FOLD(HELIX(a)) + k."""
    name = "fold_helix_add"
    novel_ops = ("FOLD", "HELIX")
    tier = 2

    def params_for(self, rng, tier):
        k_choices = {1: (1,), 2: (2, 3), 3: (4, 5)}[tier]
        k = k_choices[rng.randint(0, len(k_choices) - 1)]
        return {"k": k, "r1": "a"}

    def evaluate(self, inputs, params):
        a = inputs["registers"][params["r1"]]
        h = (om.OrderMachine.rotate_left(a) + 2) % 256  # HELIX (wraps)
        d = om.OrderMachine.digits(h)                   # FOLD
        return [d[0] + d[1] + params["k"]]

    def canonical(self, params):
        return f"OUT (FOLD (HELIX {params['r1']})) + {params['k']}"

    def naive(self, params):
        return f"OUT FOLD HELIX {params['r1']} + {params['k']}"

    def describe(self, params, phrasing=1):
        k, r1 = params["k"], params["r1"]
        if phrasing == 1:
            return (f"Read register {r1}. Apply HELIX to it. Then apply "
                    f"FOLD to the value that HELIX produces. Add {k} to "
                    f"that. Output the result.")
        return (f"Take the single register {r1}. First run HELIX over it, "
                f"then run FOLD over whatever HELIX handed back. Increase "
                f"the final number by {k} and emit it.")

    def draw_inputs(self, rng, params):
        # naive reading: HELIX(a + k) needs a + k <= 255; both readings are
        # otherwise error-free (HELIX wraps; FOLD is bounded).
        k = params["k"]
        hi = 255 - k
        if hi < 0:
            return None
        a = rng.randint(0, hi)
        return {"registers": {"a": a}, "queue": []}


class HelixPushDrainRecipe(Recipe):
    """Family B S3 (CVI-0.1): novel op + queue composition, multi-line.
    `PUSH HELIX a + k` means PUSH (HELIX (a + k)) — the '+ k' is swallowed
    into HELIX's operand unless parenthesised."""
    name = "helix_push_drain"
    novel_ops = ("HELIX",)
    tier = 3

    def params_for(self, rng, tier):
        k_choices = {1: (1,), 2: (1, 2), 3: (3, 4)}[tier]
        k = k_choices[rng.randint(0, len(k_choices) - 1)]
        return {"k": k, "r1": "a"}

    def evaluate(self, inputs, params):
        a = inputs["registers"][params["r1"]]
        h = (om.OrderMachine.rotate_left(a) + 2) % 256
        return [h + params["k"]]

    def canonical(self, params):
        return f"PUSH (HELIX {params['r1']}) + {params['k']}\nDRAIN"

    def naive(self, params):
        return f"PUSH HELIX {params['r1']} + {params['k']}\nDRAIN"

    def describe(self, params, phrasing=1):
        k, r1 = params["k"], params["r1"]
        if phrasing == 1:
            return (f"Read register {r1}. Apply HELIX to it. Add {k} to "
                    f"the value that HELIX produces. Put the result onto "
                    f"the queue. Move the entire queue to the output, "
                    f"front to back.")
        return (f"Start from register {r1}. Run HELIX over it, raise the "
                f"number it hands back by {k}, push that number into the "
                f"queue, and finally send everything in the queue, oldest "
                f"first, to the output.")

    def draw_inputs(self, rng, params):
        # intended: (rotl(a)+2)%256 + k <= 255; naive: HELIX(a + k) in
        # range and error-free (wraps).  rotl(a) in {254,255} wraps the
        # +2, so only rotl values whose +2 exceeds 255-k without wrapping
        # are excluded.
        k = params["k"]
        hi = 255 - k
        if hi < 0:
            return None
        candidates = []
        for a in range(0, hi + 1):
            rot = om.OrderMachine.rotate_left(a)
            h = (rot + 2) % 256
            if h + k <= 255:
                candidates.append(a)
        if not candidates:
            return None
        a = candidates[rng.randint(0, len(candidates) - 1)]
        return {"registers": {params["r1"]: a}, "queue": []}


RECIPES = {
    "swizzle_mul": SwizzleMulRecipe,
    "mirror_add": MirrorAddRecipe,
    "swizzle_mul_add": SwizzleMulAddRecipe,
    "splice_drain": SpliceDrainRecipe,
    "helix_mul_add": HelixMulAddRecipe,
    "nudge_add": NudgeAddRecipe,
    "fold_helix_add": FoldHelixAddRecipe,
    "helix_push_drain": HelixPushDrainRecipe,
}

FAMILY_A_RECIPES = ("swizzle_mul", "mirror_add", "swizzle_mul_add",
                    "splice_drain")
# CVI-0.1 transfer S3: different novel operators/compositions, same
# structural pattern (novel-op-with-twist + expression quirk) as Family A.
FAMILY_B_S3_RECIPES = ("fold_helix_add", "helix_push_drain")
# Default (level-0) S3 parameter spec used when no calibrated spec is
# supplied (tests, standalone generation).
DEFAULT_S3_SPEC = {"fold_helix_add": {"k": 2}, "helix_push_drain": {"k": 1}}


# ---------------------------------------------------------------------------
# Case generation
# ---------------------------------------------------------------------------

def _make_cases(task: Task, recipe: Recipe, n_public: int, n_hidden: int,
                vm: om.OrderMachine) -> None:
    """Draw public + hidden cases and mechanically verify the validity
    guarantees (canonical passes everything; naive misparse fails >=1
    public and >=2 hidden cases)."""
    rng = SeededRandom(task.case_seed)
    cases: List[Tuple[Dict[str, Any], List[int]]] = []
    seen: set = set()
    attempts = 0
    while len(cases) < n_public + n_hidden and attempts < MAX_CASE_ATTEMPTS:
        attempts += 1
        inputs = recipe.draw_inputs(rng, task.params)
        if inputs is None:
            continue
        key = json.dumps(inputs, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        expected = recipe.evaluate(inputs, task.params)
        cases.append((inputs, expected))
    if len(cases) < n_public + n_hidden:
        raise GeneratorError(
            f"task {task.task_id}: could not draw enough valid cases "
            f"({len(cases)}/{n_public + n_hidden}) after {attempts} attempts")

    public_pairs = cases[:n_public]
    hidden_pairs = cases[n_public:]

    def passes(program: str, pairs) -> bool:
        for inputs, expected in pairs:
            result = vm.run(program, inputs)
            if result.error is not None or result.output != expected:
                return False
        return True

    # canonical must pass everything
    if not passes(task.canonical_program, public_pairs + hidden_pairs):
        raise GeneratorError(
            f"task {task.task_id}: canonical program fails its own cases")

    naive_public_fails = sum(
        0 if passes(task.naive_program, [p]) else 1 for p in public_pairs)
    naive_hidden_fails = sum(
        0 if passes(task.naive_program, [p]) else 1 for p in hidden_pairs)
    if naive_public_fails < 1 or naive_hidden_fails < 2:
        raise GeneratorError(
            f"task {task.task_id}: naive misparse not discriminative "
            f"(public fails={naive_public_fails}, "
            f"hidden fails={naive_hidden_fails})")

    task.public_cases = [
        TestCase(case_id=i + 1, inputs=inp, expected_output=exp)
        for i, (inp, exp) in enumerate(public_pairs)]
    task.hidden_cases = [
        TestCase(case_id=n_public + i + 1, inputs=inp, expected_output=exp)
        for i, (inp, exp) in enumerate(hidden_pairs)]


def _build_task(task_id: str, family: str, subfamily: str, recipe_name: str,
                tier: int, seed: int, case_seed: int, phrasing: int,
                params: Optional[Dict[str, Any]] = None,
                param_overrides: Optional[Dict[str, Any]] = None,
                reuse_params: Optional[Dict[str, Any]] = None,
                reuse_cases: Optional[Tuple[List[TestCase],
                                            List[TestCase]]] = None,
                vm: Optional[om.OrderMachine] = None) -> Task:
    rng = SeededRandom(seed)
    recipe_cls = RECIPES[recipe_name]
    recipe = recipe_cls()
    if reuse_params is not None:
        params = dict(reuse_params)
    else:
        params = recipe.params_for(rng, tier)
    if param_overrides:
        params.update(param_overrides)
    task = Task(
        task_id=task_id, family=family, subfamily=subfamily,
        recipe=recipe_name, tier=tier, seed=seed, case_seed=case_seed,
        description=recipe.describe(params, phrasing=phrasing),
        params=params, phrasing=phrasing,
        canonical_program=recipe.canonical(params),
        naive_program=recipe.naive(params))
    vm = vm or om.OrderMachine()
    if reuse_cases is not None:
        task.public_cases = [TestCase(c.case_id, c.inputs, c.expected_output)
                             for c in reuse_cases[0]]
        task.hidden_cases = [TestCase(c.case_id, c.inputs, c.expected_output)
                             for c in reuse_cases[1]]
    else:
        _make_cases(task, recipe, PUBLIC_CASES_PER_TASK, HIDDEN_CASES_PER_TASK,
                    vm)
    task.difficulty = difficulty_profile(task, vm=vm)
    return task


# ---------------------------------------------------------------------------
# Per-instance difficulty stratification (CVI-0.1 refinement)
# ---------------------------------------------------------------------------

def difficulty_profile(task: Task,
                       vm: Optional[om.OrderMachine] = None) -> Dict[str, Any]:
    """Deterministic structural difficulty metadata for ONE instance.

    Pure function of the task: no randomness, no model, no selection.
    The recorded features are the structural properties suspected (from
    the CVI-0 evidence) to drive observed difficulty: which novel-op
    traps are present, whether the program must wrap an expression in
    OUT/PUSH, whether it is multi-statement, queue usage, arithmetic
    surface, phrasing variant, parameter magnitudes, and how strongly the
    naive misparse discriminates.  This metadata is NEVER participant-
    facing (public_view() drops it).
    """
    vm = vm or om.OrderMachine()
    recipe_cls = RECIPES[task.recipe]
    novel_ops = list(recipe_cls.novel_ops)
    canon = task.canonical_program
    canon_upper = canon.upper()
    lines = [ln.strip() for ln in canon.splitlines() if ln.strip()]

    def passes(program: str, cases) -> bool:
        for case in cases:
            run = vm.run(program, case.inputs)
            if run.error is not None or run.output != case.expected_output:
                return False
        return True

    naive_public_fails = sum(
        0 if passes(task.naive_program, [c]) else 1
        for c in task.public_cases)
    naive_hidden_fails = sum(
        0 if passes(task.naive_program, [c]) else 1
        for c in task.hidden_cases)

    params = dict(task.params)
    stratum_parts = []
    for key in ("k", "m", "mode"):
        if key in params:
            stratum_parts.append(f"{key}={params[key]}")
    stratum_parts.append(f"phr={task.phrasing}")
    stratum_key = task.recipe + "".join(f"[{p}]" for p in stratum_parts)

    return {
        "stratum_key": stratum_key,
        "features": {
            "recipe": task.recipe,
            "novel_ops": novel_ops,
            "n_novel_ops": len(novel_ops),
            "n_novel_op_tokens": sum(
                canon_upper.count(op) for op in novel_ops),
            "multi_statement": len(lines) > 1,
            "starts_with_out": canon_upper.lstrip().startswith("OUT"),
            "uses_queue_ops": any(op in canon_upper
                                  for op in ("PUSH", "POP", "DRAIN",
                                             "SPLICE")),
            "nested_novel_expression": sum(
                canon_upper.count(op) for op in novel_ops) > 1,
            # unary pure-value operators the CVI-0 evidence showed being
            # misread as register-writing (the "purity trap")
            "purity_trap": any(op in novel_ops
                               for op in ("MIRROR", "HELIX", "FOLD",
                                          "NUDGE")),
            "arith_op_count": sum(canon.count(ch) for ch in "+-*"),
            "params": params,
            "phrasing": task.phrasing,
            "n_public_cases": len(task.public_cases),
            "n_hidden_cases": len(task.hidden_cases),
        },
        "naive_discrimination": {
            "public_fails": naive_public_fails,
            "hidden_fails": naive_hidden_fails,
        },
        "generator_version": GENERATOR_VERSION,
    }


# ---------------------------------------------------------------------------
# Public family entry points
# ---------------------------------------------------------------------------

def generate_family_a(k: int, seed: int, tier: int = 2,
                      vm: Optional[om.OrderMachine] = None,
                      id_prefix: str = "A",
                      spec: Optional[Dict[str, Dict[str, Any]]] = None
                      ) -> List[Task]:
    """K Family-A repair tasks (pilot K=4).

    `spec` optionally pins, per recipe, the deterministic stratum
    parameters chosen by calibration (e.g. {"swizzle_mul": {"k": 3}}).
    Without a spec, parameters are drawn from the legacy tier catalog."""
    if k != len(FAMILY_A_RECIPES):
        raise GeneratorError(
            f"Family A pilot requires exactly {len(FAMILY_A_RECIPES)} tasks "
            f"(one per recipe template); got k={k}")
    rng = SeededRandom(seed)
    tasks = []
    for i, recipe_name in enumerate(FAMILY_A_RECIPES):
        task_seed = rng.next64()
        case_seed = rng.next64()
        overrides = None
        if spec and recipe_name in spec:
            overrides = dict(spec[recipe_name])
        tasks.append(_build_task(
            f"{id_prefix}-{i + 1:02d}", "A", "repair", recipe_name, tier,
            task_seed, case_seed, phrasing=1, vm=vm,
            param_overrides=overrides))
    return tasks


def generate_family_b(a_tasks: List[Task], seed: int, tier: int = 2,
                      vm: Optional[om.OrderMachine] = None,
                      s3_spec: Optional[Dict[str, Dict[str, Any]]] = None,
                      spec: Optional[Dict[str, Dict[str, Any]]] = None
                      ) -> List[Task]:
    """Small transfer batch: 2x S1 paraphrase (reworded duplicates of
    A-01 and A-02), 2x S2 novel-parameter, 2x S3 novel-composition.

    CVI-0.1: the S2 rung keeps the calibrated Family-A stratum parameters
    (`spec`) with fresh registers/cases; the S3 rung uses nested/queue
    novel compositions (fold_helix_add, helix_push_drain) selected from
    calibration strata (`s3_spec`).  Both keep the Family-A structural
    challenge (novel-op twist + expression quirk) while CVI-0's trivially
    solvable S3 is retired from the family."""
    vm = vm or om.OrderMachine()
    if len(a_tasks) < 2:
        raise GeneratorError("Family B S1 needs at least 2 Family-A tasks")
    a_swizzle = next(t for t in a_tasks if t.recipe == "swizzle_mul")
    a_mirror = next(t for t in a_tasks if t.recipe == "mirror_add")
    rng = SeededRandom(seed)
    tasks: List[Task] = []
    s3_spec = dict(s3_spec or DEFAULT_S3_SPEC)
    spec = dict(spec or {})

    def next_seed() -> int:
        return rng.next64()

    # S1: reworded duplicates (same params, same cases)
    tasks.append(_build_task(
        "B-S1-01", "B", "s1", "swizzle_mul", tier, next_seed(), next_seed(),
        phrasing=2, reuse_params=a_swizzle.params,
        reuse_cases=(a_swizzle.public_cases, a_swizzle.hidden_cases), vm=vm))
    tasks.append(_build_task(
        "B-S1-02", "B", "s1", "mirror_add", tier, next_seed(), next_seed(),
        phrasing=2, reuse_params=a_mirror.params,
        reuse_cases=(a_mirror.public_cases, a_mirror.hidden_cases), vm=vm))

    # S2: same recipes, calibrated stratum parameters, new registers /
    # fresh cases.  Register overrides are applied AFTER the spec so the
    # case inputs and the description always agree.
    s2_swizzle = _build_task(
        "B-S2-01", "B", "s2", "swizzle_mul", tier, next_seed(), next_seed(),
        phrasing=1,
        param_overrides={**spec.get("swizzle_mul", {}), "r1": "c", "r2": "d"},
        vm=vm)
    tasks.append(s2_swizzle)

    s2_mirror = _build_task(
        "B-S2-02", "B", "s2", "mirror_add", tier, next_seed(), next_seed(),
        phrasing=1, param_overrides={**spec.get("mirror_add", {}), "r1": "e"},
        vm=vm)
    tasks.append(s2_mirror)

    # S3: different novel operators, same structural pattern, harder
    # compositions (CVI-0.1 refinement — CVI-0's S3 sat at ceiling).
    for i, recipe_name in enumerate(FAMILY_B_S3_RECIPES):
        tasks.append(_build_task(
            f"B-S3-{i + 1:02d}", "B", "s3", recipe_name, tier,
            next_seed(), next_seed(), phrasing=1, vm=vm,
            param_overrides=dict(s3_spec.get(recipe_name, {}))))
    return tasks


def generate_family_c(seed: int, tier: int = 2,
                      vm: Optional[om.OrderMachine] = None,
                      spec: Optional[Dict[str, Dict[str, Any]]] = None
                      ) -> List[Task]:
    """Family C: fresh seeds, unseen parameter draws, same generator
    config (including the calibrated spec) as Family A.  Call ONLY after
    all interaction phases have completed (protocol.py enforces this at
    the harness level)."""
    return generate_family_a(len(FAMILY_A_RECIPES), seed, tier=tier, vm=vm,
                             id_prefix="C", spec=spec)


def generate_calibration_set(seed: int, tier: int = 2,
                             vm: Optional[om.OrderMachine] = None
                             ) -> List[Task]:
    """Calibration instances: same recipes, FRESH seeds, used only for
    difficulty calibration (pilot engineering evidence, never mixed with
    the pilot instances)."""
    return generate_family_a(len(FAMILY_A_RECIPES), seed, tier=tier, vm=vm)


def generate_stratified_calibration_batch(
        catalog: Dict[str, Any], seed: int,
        vm: Optional[om.OrderMachine] = None) -> List[Task]:
    """One fresh calibration instance per (recipe, stratum) entry of the
    catalog, drawn from a disposable seed.  Used ONLY by calibration; the
    instances are preserved as calibration evidence and never appear in an
    experimental family.  Task ids are globally unique across the batch
    (the recipe and stratum live in params / difficulty metadata)."""
    vm = vm or om.OrderMachine()
    rng = SeededRandom(seed)
    tasks: List[Task] = []
    counter = 0
    for recipe_name, strata in catalog.items():
        for stratum in strata:
            counter += 1
            task_seed = rng.next64()
            case_seed = rng.next64()
            tasks.append(_build_task(
                f"CAL-{counter:03d}", "CAL", "baseline_stratum",
                recipe_name, 2, task_seed, case_seed, phrasing=1, vm=vm,
                param_overrides=dict(stratum)))
    return tasks


def serialize_tasks(tasks: List[Task]) -> str:
    return json.dumps([t.to_dict() for t in tasks], indent=2, sort_keys=True)


def tasks_checksum(tasks: List[Task]) -> str:
    payload = serialize_tasks(tasks)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
