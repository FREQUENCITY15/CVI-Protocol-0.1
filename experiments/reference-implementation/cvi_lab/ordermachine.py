"""
OrderMachine — a deterministic, text-based, stateful virtual machine with a
deliberately novel instruction set.

This module implements the environment specified in the authoritative
CVI-1 experiment design (section 2): registers + queue, ~15 instructions,
three or more novel operators with nonstandard semantics, deterministic
execution, explicit syntax validation, deterministic error classes,
maximum execution-step protection, versioned submissions, and reproducible
behaviour.

The VM is fully deterministic: it consumes no randomness at runtime.
Seeds live exclusively in the task generator (generator.py).

Participant-facing semantics are documented in PARTICIPANT_SPEC below.
Nothing else in this module is part of the permitted participant material.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
# Constants (documented in the participant spec)
# ---------------------------------------------------------------------------

REGISTERS = ("a", "b", "c", "d", "e", "f")
VALUE_MIN = 0
VALUE_MAX = 255
BITS = 8
QUEUE_CAPACITY = 64
MAX_STEPS_DEFAULT = 10_000
DIGIT_WIDTH = 2

NOVEL_OPS = ("SWIZZLE", "MIRROR", "SPLICE", "HELIX", "FOLD", "NUDGE")
NOVEL_ARITY = {"SWIZZLE": 2, "MIRROR": 1, "SPLICE": 2, "HELIX": 1,
               "FOLD": 1, "NUDGE": 1}
INSTRUCTIONS = ("SET", "ADD", "SUB", "MUL", "DIV", "OUT", "PUSH", "POP",
                "DRAIN")

# Error classes — deterministic, stable identifiers.
ERR_SYNTAX = "SYNTAX"
ERR_UNDEF_REGISTER = "UNDEF_REGISTER"
ERR_UNDERFLOW = "UNDERFLOW"
ERR_OVERFLOW = "OVERFLOW"
ERR_DIVZERO = "DIVZERO"
ERR_QEMPTY = "QEMPTY"
ERR_QFULL = "QFULL"
ERR_STEP_LIMIT = "STEP_LIMIT"
ERR_BAD_LITERAL = "BAD_LITERAL"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MachineError:
    """A deterministic error raised during parsing or execution."""
    error_class: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    instruction_index: Optional[int] = None
    step: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OrderMachineError(Exception):
    def __init__(self, err: MachineError):
        super().__init__(err.message)
        self.err = err


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Token:
    kind: str          # 'word' | 'int' | '+' | '-' | '*' | '(' | ')'
    text: str
    line: int
    column: int


def tokenize(program: str) -> List[Token]:
    """Tokenize a program. Newlines are kept as separators so the parser
    can enforce one instruction per line. Raises OrderMachineError(SYNTAX)
    on bad tokens."""
    tokens: List[Token] = []
    lines = program.split("\n")
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.split("#", 1)[0]  # strip comments
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            if ch.isspace():
                i += 1
                continue
            if ch in "+-*()":
                tokens.append(Token(ch, ch, lineno, i + 1))
                i += 1
                continue
            if ch.isdigit():
                j = i
                while j < n and line[j].isdigit():
                    j += 1
                tokens.append(Token("int", line[i:j], lineno, i + 1))
                i = j
                continue
            if ch.isalpha():
                j = i
                while j < n and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                tokens.append(Token("word", line[i:j], lineno, i + 1))
                i = j
                continue
            raise OrderMachineError(MachineError(
                ERR_SYNTAX, f"unexpected character {ch!r}", line=lineno,
                column=i + 1))
        if lineno < len(lines):
            tokens.append(Token("newline", "\\n", lineno, i + 1))
    return tokens


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------

class Node:
    pass


@dataclass
class IntLit(Node):
    value: int


@dataclass
class Reg(Node):
    name: str


@dataclass
class BinOp(Node):
    op: str
    left: Node
    right: Node


@dataclass
class Novel(Node):
    op: str
    operands: List[Node]
    # For binary novel ops, operand 1 is an atom and operand 2 is a full
    # expression. This deliberate asymmetry is part of the language's
    # documented precedence rules.


@dataclass
class Stmt(Node):
    op: str
    operands: List[Node]


@dataclass
class Program:
    statements: List[Node]
    source: str


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class _Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self) -> Optional[Token]:
        tok = self.peek()
        if tok is not None:
            self.pos += 1
        return tok

    def error(self, message: str, tok: Optional[Token] = None) -> None:
        t = tok or self.peek()
        raise OrderMachineError(MachineError(
            ERR_SYNTAX, message,
            line=t.line if t else None, column=t.column if t else None))

    # ---- expression grammar -------------------------------------------------
    #
    # expr   := novel_expr | arith_expr
    # arith  := term (('+' | '-') term)*            left-associative
    # term   := atom ('*' atom)*                    left-associative
    # atom   := register | literal | '(' expr ')'
    # novel  := NOVEL_OP operand...   (novel ops must BEGIN an expression;
    #           the last operand greedily consumes the rest of the
    #           expression; a binary novel op's FIRST operand is an atom)
    #
    # Consequence (the novel precedence rules, deliberately counterintuitive):
    #   SWIZZLE a b + 1   means  SWIZZLE(a, b + 1)
    #   (SWIZZLE a b) + 1 means  SWIZZLE(a, b) then add 1
    #   1 + SWIZZLE a b   is a SYNTAX error

    def parse_expr(self) -> Node:
        tok = self.peek()
        if tok is None:
            self.error("expected an expression, found end of line")
        if tok.kind == "word" and tok.text.upper() in NOVEL_OPS:
            return self.parse_novel()
        return self.parse_arith()

    def parse_novel(self) -> Node:
        op_tok = self.next()
        assert op_tok is not None
        op = op_tok.text.upper()
        arity = NOVEL_ARITY[op]
        operands: List[Node] = []
        if arity == 2:
            operands.append(self.parse_atom())
        operands.append(self.parse_expr())
        if op == "SWIZZLE" and not isinstance(operands[0], Reg):
            self.error("SWIZZLE's first operand must be a register (a-f) "
                       "that receives the result", op_tok)
        return Novel(op, operands)

    def parse_arith(self) -> Node:
        node = self.parse_term()
        while True:
            tok = self.peek()
            if tok is not None and tok.kind in ("+", "-"):
                self.next()
                right = self.parse_term()
                node = BinOp(tok.kind, node, right)
            else:
                break
        return node

    def parse_term(self) -> Node:
        node = self.parse_atom()
        while True:
            tok = self.peek()
            if tok is not None and tok.kind == "*":
                self.next()
                right = self.parse_atom()
                node = BinOp("*", node, right)
            else:
                break
        return node

    def parse_atom(self) -> Node:
        tok = self.peek()
        if tok is None:
            self.error("expected a value, found end of line")
        if tok.kind == "int":
            self.next()
            value = int(tok.text)
            if not (VALUE_MIN <= value <= VALUE_MAX):
                raise OrderMachineError(MachineError(
                    ERR_BAD_LITERAL,
                    f"literal {value} outside {VALUE_MIN}..{VALUE_MAX}",
                    line=tok.line, column=tok.column))
            return IntLit(value)
        if tok.kind == "word" and tok.text in REGISTERS:
            self.next()
            return Reg(tok.text)
        if tok.kind == "(":
            self.next()
            node = self.parse_expr()
            close = self.next()
            if close is None or close.kind != ")":
                self.error("expected ')' to close parenthesised expression",
                           close or tok)
            return node
        if tok.kind == "word" and tok.text.upper() in NOVEL_OPS:
            self.error(
                f"novel operator {tok.text.upper()} must begin the expression; "
                "it cannot appear mid-expression without parentheses", tok)
        self.error(f"expected a register or literal, found {tok.text!r}", tok)
        raise AssertionError("unreachable")

    # ---- statements ---------------------------------------------------------

    def parse_statement(self) -> Node:
        tok = self.peek()
        if tok is None:
            self.error("expected an instruction, found end of line")
        if tok.kind == "word" and tok.text.upper() in INSTRUCTIONS:
            self.next()
            op = tok.text.upper()
            operands: List[Node] = []
            if op == "SET" or op == "ADD" or op == "SUB" or op == "MUL" \
                    or op == "DIV":
                operands.append(self.parse_reg())
                operands.append(self.parse_expr())
            elif op == "OUT" or op == "PUSH":
                operands.append(self.parse_expr())
            elif op == "POP":
                operands.append(self.parse_reg())
            elif op == "DRAIN":
                pass
            return Stmt(op, operands)
        # A bare expression statement is allowed: its value is discarded but
        # its side effects (novel operators write registers / push the queue)
        # still happen.
        return self.parse_expr()

    def parse_reg(self) -> Node:
        tok = self.peek()
        if tok is None or tok.kind != "word" or tok.text not in REGISTERS:
            self.error("expected a register name (a-f)", tok)
        self.next()
        return Reg(tok.text)


def parse_program(program: str) -> Program:
    tokens = tokenize(program)
    parser = _Parser(tokens)
    statements: List[Node] = []
    while True:
        while parser.peek() is not None and parser.peek().kind == "newline":
            parser.next()
        if parser.peek() is None:
            break
        statements.append(parser.parse_statement())
        nxt = parser.peek()
        if nxt is not None and nxt.kind != "newline":
            parser.error(f"unexpected trailing tokens on instruction line "
                         f"({nxt.text!r}) — one instruction per line", nxt)
    return Program(statements, program)


# ---------------------------------------------------------------------------
# Machine
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    output: List[int]
    error: Optional[MachineError]
    steps: int
    final_registers: Dict[str, int]
    final_queue: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output": list(self.output),
            "error": self.error.to_dict() if self.error else None,
            "steps": self.steps,
            "final_registers": dict(self.final_registers),
            "final_queue": list(self.final_queue),
        }


class OrderMachine:
    """A fresh machine instance per execution. No state persists between
    executions: each run starts from the provided inputs."""

    def __init__(self, max_steps: int = MAX_STEPS_DEFAULT):
        self.max_steps = max_steps

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def bit_reverse(value: int) -> int:
        result = 0
        for _ in range(BITS):
            result = (result << 1) | (value & 1)
            value >>= 1
        return result

    @staticmethod
    def rotate_left(value: int) -> int:
        return ((value << 1) | (value >> (BITS - 1))) & 0xFF

    @staticmethod
    def popcount(value: int) -> int:
        return bin(value).count("1")

    @staticmethod
    def digits(value: int) -> List[int]:
        """Two-digit, zero-padded digit sequence of a value."""
        assert VALUE_MIN <= value <= VALUE_MAX
        return [value // 10, value % 10]

    # -- execution -----------------------------------------------------------

    def run(self, program: str, inputs: Dict[str, Any],
            max_steps: Optional[int] = None) -> RunResult:
        limit = max_steps if max_steps is not None else self.max_steps
        try:
            parsed = parse_program(program)
        except OrderMachineError as exc:
            return RunResult([], exc.err, 0, {}, [])

        regs: Dict[str, int] = {r: 0 for r in REGISTERS}
        for name, value in (inputs.get("registers") or {}).items():
            if name not in REGISTERS:
                return RunResult([], MachineError(
                    ERR_UNDEF_REGISTER, f"unknown input register {name!r}"),
                    0, {}, [])
            if not isinstance(value, int) or not (VALUE_MIN <= value <= VALUE_MAX):
                return RunResult([], MachineError(
                    ERR_BAD_LITERAL, f"input value for {name} out of range"),
                    0, {}, [])
            regs[name] = value
        queue: List[int] = list(inputs.get("queue") or [])
        if len(queue) > QUEUE_CAPACITY:
            return RunResult([], MachineError(
                ERR_QFULL, f"initial queue exceeds capacity {QUEUE_CAPACITY}"),
                0, {}, [])
        output: List[int] = []
        steps = 0

        def eval_node(node: Node, line: Optional[int] = None) -> int:
            nonlocal steps, output
            if isinstance(node, IntLit):
                return node.value
            if isinstance(node, Reg):
                if node.name not in regs:
                    raise OrderMachineError(MachineError(
                        ERR_UNDEF_REGISTER, f"unknown register {node.name!r}",
                        line=line))
                return regs[node.name]
            if isinstance(node, BinOp):
                left = eval_node(node.left, line)
                right = eval_node(node.right, line)
                if node.op == "+":
                    value = left + right
                    if value > VALUE_MAX:
                        raise OrderMachineError(MachineError(
                            ERR_OVERFLOW,
                            f"{left} + {right} = {value} > {VALUE_MAX}",
                            line=line))
                    return value
                if node.op == "-":
                    value = left - right
                    if value < VALUE_MIN:
                        raise OrderMachineError(MachineError(
                            ERR_UNDERFLOW,
                            f"{left} - {right} = {value} < {VALUE_MIN}",
                            line=line))
                    return value
                if node.op == "*":
                    value = left * right
                    if value > VALUE_MAX:
                        raise OrderMachineError(MachineError(
                            ERR_OVERFLOW,
                            f"{left} * {right} = {value} > {VALUE_MAX}",
                            line=line))
                    return value
                raise AssertionError("unknown binop")
            if isinstance(node, Novel):
                op = node.op
                args = [eval_node(o, line) for o in node.operands]
                if op == "SWIZZLE":
                    target = node.operands[0].name
                    if args[1] == 0:
                        raise OrderMachineError(MachineError(
                            ERR_UNDERFLOW, "SWIZZLE of 0", line=line))
                    regs[target] = args[1] - 1
                    return regs[target]
                if op == "MIRROR":
                    rev = self.bit_reverse(args[0])
                    if rev == 255:
                        raise OrderMachineError(MachineError(
                            ERR_OVERFLOW, "MIRROR result would exceed 255",
                            line=line))
                    return rev + 1
                if op == "SPLICE":
                    d1 = self.digits(args[0])
                    d2 = self.digits(args[1])
                    interleaved = [d1[0], d2[0], d1[1], d2[1]]
                    surviving = [v for i, v in enumerate(interleaved)
                                 if (i + 1) % 3 != 0]
                    for v in surviving:
                        if len(queue) >= QUEUE_CAPACITY:
                            raise OrderMachineError(MachineError(
                                ERR_QFULL, "queue full during SPLICE",
                                line=line))
                        queue.append(v)
                    return len(surviving)
                if op == "HELIX":
                    return (self.rotate_left(args[0]) + 2) % 256
                if op == "FOLD":
                    d = self.digits(args[0])
                    return d[0] + d[1]
                if op == "NUDGE":
                    value = args[0] + self.popcount(args[0])
                    if value > VALUE_MAX:
                        raise OrderMachineError(MachineError(
                            ERR_OVERFLOW, "NUDGE result exceeds 255",
                            line=line))
                    return value
                raise AssertionError("unknown novel op")
            raise AssertionError("unknown node")

        current_index: Optional[int] = None
        try:
            for index, stmt in enumerate(parsed.statements):
                current_index = index
                if isinstance(stmt, Stmt):
                    op = stmt.op
                    if op == "SET":
                        target = stmt.operands[0].name
                        regs[target] = eval_node(stmt.operands[1])
                    elif op == "ADD":
                        target = stmt.operands[0].name
                        value = regs[target] + eval_node(stmt.operands[1])
                        if value > VALUE_MAX:
                            raise OrderMachineError(MachineError(
                                ERR_OVERFLOW, "ADD result exceeds 255"))
                        regs[target] = value
                    elif op == "SUB":
                        target = stmt.operands[0].name
                        value = regs[target] - eval_node(stmt.operands[1])
                        if value < VALUE_MIN:
                            raise OrderMachineError(MachineError(
                                ERR_UNDERFLOW, "SUB result below 0"))
                        regs[target] = value
                    elif op == "MUL":
                        target = stmt.operands[0].name
                        value = regs[target] * eval_node(stmt.operands[1])
                        if value > VALUE_MAX:
                            raise OrderMachineError(MachineError(
                                ERR_OVERFLOW, "MUL result exceeds 255"))
                        regs[target] = value
                    elif op == "DIV":
                        target = stmt.operands[0].name
                        divisor = eval_node(stmt.operands[1])
                        if divisor == 0:
                            raise OrderMachineError(MachineError(
                                ERR_DIVZERO, "DIV by zero"))
                        regs[target] = regs[target] // divisor
                    elif op == "OUT":
                        output.append(eval_node(stmt.operands[0]))
                    elif op == "PUSH":
                        if len(queue) >= QUEUE_CAPACITY:
                            raise OrderMachineError(MachineError(
                                ERR_QFULL, "queue full"))
                        queue.append(eval_node(stmt.operands[0]))
                    elif op == "POP":
                        if not queue:
                            raise OrderMachineError(MachineError(
                                ERR_QEMPTY, "POP on empty queue"))
                        regs[stmt.operands[0].name] = queue.pop(0)
                    elif op == "DRAIN":
                        while queue:
                            output.append(queue.pop(0))
                    else:
                        raise AssertionError("unknown instruction")
                else:
                    # bare expression statement: value discarded
                    eval_node(stmt)
                steps += 1
                if steps > limit:
                    raise OrderMachineError(MachineError(
                        ERR_STEP_LIMIT, f"step limit {limit} exceeded",
                        instruction_index=index, step=steps))
        except OrderMachineError as exc:
            err = MachineError(
                error_class=exc.err.error_class,
                message=exc.err.message,
                line=exc.err.line,
                column=exc.err.column,
                instruction_index=(
                    exc.err.instruction_index
                    if exc.err.instruction_index is not None
                    else current_index),
                step=exc.err.step if exc.err.step is not None else steps)
            return RunResult(list(output), err, steps, dict(regs),
                             list(queue))
        return RunResult(list(output), None, steps, dict(regs), list(queue))


# ---------------------------------------------------------------------------
# Versioned submissions
# ---------------------------------------------------------------------------

@dataclass
class SubmissionRecord:
    submission_id: str
    version: int
    timestamp_iso: str
    program: str
    public_result: Optional[Dict[str, Any]] = None
    hidden_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SubmissionLog:
    """Read-only, append-only version history for one task instance."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self._entries: List[SubmissionRecord] = []

    def submit(self, program: str,
               public_result: Optional[Dict[str, Any]] = None,
               hidden_score: Optional[float] = None) -> SubmissionRecord:
        version = len(self._entries) + 1
        record = SubmissionRecord(
            submission_id=hashlib.sha256(
                f"{self.task_id}:{version}:{program}".encode()).hexdigest(),
            version=version,
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            program=program,
            public_result=public_result,
            hidden_score=hidden_score)
        self._entries.append(record)
        return record

    def entries(self) -> List[SubmissionRecord]:
        # Defensive copy: version history is read-only.
        return list(self._entries)


# ---------------------------------------------------------------------------
# Participant-facing specification sheet (ONLY permitted semantics)
# ---------------------------------------------------------------------------

PARTICIPANT_SPEC = """\
# OrderMachine — Language Specification

OrderMachine is a small deterministic machine you control by writing a text
program. A program is executed on a given set of inputs, and its result is
the sequence of numbers it emits (its output stream).

## Data

* Six registers named `a b c d e f`. Each register holds one whole number
  from 0 to 255. Registers start at the input values for the task (unspecified
  registers start at 0).
* A queue: a FIFO list of whole numbers 0-255, holding at most 64 elements.
  It may start pre-filled by the task inputs.
* An output stream: every number the program emits, in order.

## Program text

One instruction per line. Blank lines are ignored. `#` starts a comment.
Instructions are written in UPPERCASE; register names are lowercase.

## Basic instructions

* `SET r expr` — store the value of expr into register r.
* `ADD r expr` — r := r + value(expr). Error OVERFLOW if above 255.
* `SUB r expr` — r := r - value(expr). Error UNDERFLOW if below 0.
* `MUL r expr` — r := r * value(expr). Error OVERFLOW if above 255.
* `DIV r expr` — r := r / value(expr), rounded down. Error DIVZERO if 0.
* `OUT expr` — append value(expr) to the output stream.
* `PUSH expr` — append value(expr) to the back of the queue. Error QFULL at 64.
* `POP r` — move the front queue element into r. Error QEMPTY if empty.
* `DRAIN` — move every queue element, in front-to-back order, to the output
  stream.

## Expressions

Expressions combine registers, literals (0-255), `+ - *`, parentheses, and
the novel operators below. Every intermediate value must stay in 0-255.

## Novel operators

* `SWIZZLE x y` — the operands are conceptually swapped, and the left one is
  decremented: register x receives (y - 1). Error UNDERFLOW if y is 0.
  Example: `SWIZZLE a b` with b=9 sets a=8.
* `MIRROR expr` — computes: reverse the 8 binary digits of the operand's
  value, then add 1. Example: for the value 1 (00000001) the reversal is
  128 (10000000), so MIRROR gives 129. The result is a value handed to the
  surroundings; no register is modified.
* `SPLICE x y` — each value is written as two digits (zero-padded, so 7 is
  07). The four digits are interleaved: tens of x, tens of y, units of x,
  units of y. Then every third element of that four-element list is removed.
  The surviving three numbers are pushed onto the queue, in order.
  Example: SPLICE with x=12, y=34: digits 1,2 and 3,4; interleaved 1,3,2,4;
  remove every third (the 2); queue receives 1,3,4.
* `HELIX expr` — computes: rotate the 8 binary digits of the operand's
  value one step left (the leftmost digit wraps to the right), then add 2.
  Values above 255 wrap around (subtract 256). No register is modified.
* `FOLD expr` — computes the sum of the operand's two digits.
  Example: FOLD of 34 is 7. No register is modified.
* `NUDGE expr` — computes: the operand's value plus the number of 1-digits
  in its 8-bit binary form. Example: for 7 (00000111) the result is 10.
  Error OVERFLOW if the result would be above 255. No register is modified.

Each novel operator computes a value, which it hands to its surroundings.

## Precedence rules (read carefully — they are unusual)

1. A novel operator must START the expression it appears in. It may not
   appear in the middle of an arithmetic expression unless wrapped in
   parentheses.
2. A novel operator's LAST operand swallows everything written to its right
   up to the end of the expression (or its closing parenthesis).
3. A two-operand novel operator's FIRST operand must be a single register,
   literal, or parenthesised expression.

Consequences:

* `SWIZZLE a b + 1` means SWIZZLE with operands a and (b + 1).
* `(SWIZZLE a b) + 1` means: apply SWIZZLE to a and b first, then add 1 to
  the value it produced.
* `1 + SWIZZLE a b` is a SYNTAX error.
* `MIRROR a + 1` means MIRROR of (a + 1). To add 1 after mirroring, write
  `(MIRROR a) + 1`.
* A novel operator may stand alone as a statement; its value is discarded
  but any side effects (SWIZZLE's register write, SPLICE's queue pushes)
  still happen.

## Errors

When a program cannot finish, execution stops and an error class is
reported: SYNTAX, UNDEF_REGISTER, UNDERFLOW, OVERFLOW, DIVZERO, QEMPTY,
QFULL, STEP_LIMIT, BAD_LITERAL.

## Checking your program

A program is checked by running it on example inputs and comparing its
output stream with the expected stream. A run is correct only if the whole
output stream matches, in order.
"""


def write_spec_sheet(path: str) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(PARTICIPANT_SPEC)
    return path
