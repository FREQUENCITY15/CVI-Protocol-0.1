# CVI-0 — Pilot Laboratory

The first pilot for the **Causally Verified Intelligence (CVI)** discriminative
experiment design.  This is a **pilot only**: one pinned model, three arms
(S / S′ / C), K = 4 interaction tasks, small retention / transfer /
hidden-verification families.  It is not a scientific validation of CVI.

Authoritative design sources (read-only copies): `source/`.

## What is here

| Path | Purpose |
|---|---|
| `cvi_lab/ordermachine.py` | OrderMachine VM (15 instructions, 6 novel operators, deterministic errors, step protection, versioning) + the participant spec sheet |
| `cvi_lab/generator.py` | Seeded procedural generation of Families A / B (S1/S2/S3) / C |
| `cvi_lab/grader.py` | Public vs hidden grading; the only permitted feedback is per-case PASS/FAIL + error class |
| `cvi_lab/participant.py` | Stateless per-call LLM client (imports no protected module), usage tracker, runaway guard |
| `cvi_lab/arms.py` | Arms S, S′, C with code-enforced context boundaries and feedback rules |
| `cvi_lab/protocol.py` | State machine that refuses to generate Family C before all interaction phases complete |
| `cvi_lab/metrics.py` | Measurement vector (S0, G_F, S_ret, M, S_tr, S_ver, gaming index, tokens, calls, time); undefined = JSON null |
| `cvi_lab/evidence.py` | No-overwrite run directories, manifest.json, sha256_manifest.txt |
| `tests/` | 90+ deterministic tests including firewall/security tests |
| `run_pilot.py` | CLI: `selftest`, `calibrate`, `run`, `finalize` |
| `runs/` | Evidence packages (raw evidence first; interpretation last) |

## Experimental firewall (enforced in code)

* The participant client (`participant.py`) imports **no** protected module.
* Participant prompts are built only from `Task.public_view()` (description +
  public examples) — never hidden cases, seeds, parameters, or programs.
* Arm C feedback is built only by `grader.feedback_block()` (case id +
  PASS/FAIL + error class).  Hidden results never enter any participant text.
* Family C generation is gated by the protocol state machine.
* Every phase of every arm runs in a fresh session; no messages cross a
  phase boundary.  The test suite proves all of this mechanically.

## Usage

```bash
python3 run_pilot.py selftest     # deterministic local tests (no API)
python3 run_pilot.py calibrate    # calibrate difficulty into 0.30-0.80
python3 run_pilot.py run          # full pilot (selftest runs first)
# compose CVI_0_Pilot_Report.md, then:
python3 run_pilot.py finalize <run_id>
```

The participant model is pinned in `cvi_lab/config.py` (default:
`deepseek-v4-pro` at the DeepSeek Anthropic-compatible endpoint,
temperature 0).  The API key is read from `$CVI_DEEPSEEK_API_KEY` or the
harness credential store at run time and is never written to disk.

## Reproducibility

* All randomness comes from a splitmix64 PRNG (`generator.SeededRandom`) —
  no library RNG, stable across Python versions.
* Seeds, full task instances (public + hidden), checksums, prompts,
  transcripts, submissions, environment logs, scores, metrics, and API
  usage are preserved in the run directory with a SHA-256 manifest.
* Run directories are never overwritten.

## Integrity rules honored by this implementation

* Never treat a successful retry as retention, retention as
  generalisation, generalisation as hidden verification, or self-report as
  evidence of learning.
* Calibration runs are pilot engineering evidence, preserved and reported.
* If S or S′ beats C, it is preserved and reported as such.
