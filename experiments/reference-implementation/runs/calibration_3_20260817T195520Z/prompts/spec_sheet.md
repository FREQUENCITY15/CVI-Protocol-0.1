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
