---
name: srs-gap-seeder
description: Seed intentional, labeled gaps between an SRS use-case spec and its source code, so a gap-detection / SRS-vs-code consistency checker can be tested on a known ground truth. Use this skill whenever the user wants to "create gaps", "seed gaps", "tạo gap", "gen test data cho gap detector", or asks to fabricate mismatch / missing / surplus discrepancies between files in `uc_specs/` (or any SRS folder) and `src/` for a specific UC. Trigger this skill even when the user only mentions one of the keywords (mismatch, missing, surplus, gap, match, UC-XX, findgap.md) — it is the right tool for any workflow that produces a new SRS file plus matching code edits as a labeled fixture for a PR-time consistency check.
---

# SRS Gap Seeder

Seed a controlled set of gaps between an SRS use-case spec and its source code so a downstream gap detector can be evaluated against a known ground truth.

## Gap types — exact wording of the system under test

These are the four gap types the user's detector emits. Use the labels **verbatim and lowercase** in any output that may be consumed by tooling (especially the ground-truth table at the end of the seeded spec):

| Label      | Meaning                                                  |
|------------|----------------------------------------------------------|
| `match`    | Code implements the SRS requirement correctly.           |
| `mismatch` | Code implements the requirement but differs from SRS.    |
| `missing`  | SRS specifies a requirement; code does not implement it. |
| `surplus`  | Code implements something the SRS does not mention.      |

This skill **seeds** `mismatch`, `missing`, and `surplus`. It does **not** seed `match`: `match` is the baseline — the parts of the UC that are already aligned and stay aligned. Whatever in the original spec/code is correctly paired remains a `match` after this skill runs, and that is exactly what the detector should classify as such (true-negative coverage). Do not invent extra `match` entries; they are produced naturally by everything you don't touch.

## Output of one run

1. A new SRS file `<srs_folder>/<ucid_lower>_findgap.md` describing the UC the way the *new* spec sees it.
2. Code edits inside `<code_root>/` so that, when the detector diffs this new spec against the code, exactly the requested number of each gap type appears.
3. A hidden ground-truth block at the bottom of the new SRS file, listing the seeded gaps for the human reviewer.

The original spec for the UC must not be modified — keep it for historical comparison.

---

## Step 0 — Collect parameters

Before doing anything else, make sure the following are known. If any are missing, ask the user **once**, in a single message, with all questions together:

- **UC ID** (e.g. `UC-01`, `UC-07`). Used to locate the original spec and to name the new file.
- **Number of `mismatch` gaps** to seed (default: 2).
- **Number of `missing` gaps** to seed (default: 2).
- **Number of `surplus` gaps** to seed (default: 1).
- **SRS folder** (default: `uc_specs/`) and **code root** (default: `src/`), in case the project uses different paths.
- **Language preference for the new SRS file** (default: match the language of the existing spec).

Do not invent values. If the original spec for the requested UC cannot be located, stop and tell the user — don't guess at which file represents the UC.

---

## Step 1 — Investigate (read-only)

Do not modify anything yet. Produce an investigation report containing:

1. A summary of the existing UC spec: actor, preconditions, main flow, alternative flows, business rules, inputs/outputs, validation, error cases.
2. Every file in the code root that implements this UC (controller, service, repository, DTO, validator, route, test, etc.). For each file, one line on its role.
3. A spec-vs-code alignment table for the **current** state. Each row is one requirement; mark whether spec and code currently agree. The rows that already agree will become `match` entries after this skill runs (they are not seeded — they are preserved).

Print this report and **stop**. Wait for the user to confirm the UC scope is correct before continuing. The whole skill depends on this scope being right; a wrong scope means useless fixtures.

---

## Step 2 — Design the gaps (still no code edits)

Create the new SRS file at `<srs_folder>/<ucid_lower>_findgap.md` (e.g. `uc_specs/uc01_findgap.md`).

Write it as a **real SRS document** — same sections, tone, and level of detail as the original spec. Do not annotate gaps inside the spec body, do not write "this is a mismatch" inline, do not leave TODOs. A reader who doesn't know about this skill should not be able to tell the file was generated as a fixture.

Design the gaps so that, once Step 3 edits the code, the diff between this new spec and the code yields exactly the requested counts. Spread the gaps across different aspects of the UC — do not pile them all onto one field or one rule. Good axes to pick from:

- Validation rules (length, regex, required vs optional)
- Business rules / branching conditions
- Response shape (field names, types, nesting)
- Error handling (status codes, error messages, error codes)
- Flow steps (ordering, additional preconditions)
- Naming (endpoint paths, parameter names)
- Side effects (logging, events, notifications)

Design constraint per gap type:

- **`mismatch`** — pick something already present in both the original spec and the code, then change the spec wording in the new file so the detail differs from what the code does. After Step 3, the code will *still implement* this requirement, just differently.
- **`missing`** — add a requirement in the new spec that the current code does not satisfy. In Step 3 you will *remove or avoid implementing* this in code.
- **`surplus`** — leave a feature/field/endpoint out of the new spec entirely. In Step 3 you will *add* this to code.

At the very end of the new SRS file, append a hidden ground-truth block. Use an HTML comment fence so it is visually marked as "not part of the spec":

```markdown
<!--
INTERNAL: GAP DESIGN — REMOVE BEFORE PRODUCTION
This block is the ground truth for the gap-detection evaluator.
Do NOT feed this section to the detector under test.

| # | type     | spec location (this file)         | code location (after Step 3)              | description |
|---|----------|-----------------------------------|-------------------------------------------|-------------|
| 1 | mismatch | <heading / line ref>              | <file:line>                               | <one line>  |
| 2 | mismatch | ...                               | ...                                       | ...         |
| 3 | missing  | ...                               | (intentionally absent in code)            | ...         |
| 4 | missing  | ...                               | (intentionally absent in code)            | ...         |
| 5 | surplus  | (intentionally absent in spec)    | <file:line>                               | ...         |
-->
```

Use the labels exactly as shown — lowercase, no quotes, no other variants. The detector evaluator may parse this table directly.

Print the new spec file path and the ground-truth table to the user, then **stop and ask for "GO"** before touching code. Reason: `missing` and `surplus` are easy to invert by accident, and rolling back code edits is more painful than rewriting a markdown file.

---

## Step 3 — Edit code to match the design

Only after the user confirms, modify files inside the code root so the gaps materialize exactly as designed.

Rules:

- For each `mismatch`, change the code so the relevant detail diverges from what the new spec says — do not also remove it.
- For each `missing`, ensure the code does not implement the requirement. If the current code already implements it, remove or weaken just that part. Do not delete unrelated code.
- For each `surplus`, add the feature in code. It must compile and not break existing tests. If a small test update is unavoidable, keep it minimal and explain it.
- Do not touch the original UC spec file.
- Do not refactor anything outside the UC's scope — every unrelated change creates noise the detector might pick up as additional false gaps.
- Keep edits as small as possible.

Suggested commit layout (only commit if the repo's workflow expects it; otherwise leave changes staged):

- Commit A: `docs(<ucid>): add <ucid>_findgap.md as gap-seeded SRS fixture`
- Commit B: `chore(<ucid>): seed gap fixtures in code for detector evaluation`

---

## Step 4 — Self-check and report

Print a final checklist and a diff summary:

- [ ] `<srs_folder>/<ucid_lower>_findgap.md` exists and reads as a normal SRS.
- [ ] Ground-truth comment block at end of file lists exactly N `mismatch` + M `missing` + K `surplus` rows (matching the user's request). All labels lowercase.
- [ ] Each row in the ground-truth table points to a real file and (where applicable) a real line.
- [ ] Original UC spec untouched.
- [ ] Project still builds; existing tests still pass (or only minimally adjusted, with reason noted).
- [ ] Files added / modified / deleted — list them, grouped by which gap they implement.

If any item fails, fix it before declaring done.

---

## Behavior notes

- Accept any non-negative integers for the gap counts (e.g. "5 mismatch, 0 missing, 3 surplus"). Do not enforce the 2/2/1 default. Total gaps = N + M + K can be any value ≥ 1.
- Never seed `match` — it is the natural state of everything not touched. If the user asks to "seed N match cases", clarify: matches are preserved automatically, the N they should care about is `mismatch` + `missing` + `surplus`.
- If the user runs the skill twice for the same UC, place the new file as `<ucid_lower>_findgap_v2.md`, `_v3.md`, etc., and never overwrite a previous fixture without explicit permission. Old fixtures may already be referenced by detector evaluation runs.
- If the user explicitly says "skip the confirmation step, just do it", you may merge Step 2 and Step 3 into a single uninterrupted run, but still produce the same artifacts and the same final checklist.
- `surplus` gaps are the riskiest: they add live code. Prefer adding them as small, isolated pieces (an extra optional response field, a debug-only endpoint behind an existing router, a new helper wired into one call site) rather than features that touch multiple modules.
- Never embed the words `match`, `mismatch`, `missing`, or `surplus` inside the spec body or in code comments — only inside the hidden ground-truth block. The detector must have no shortcut to the answer via keyword matching.
- The point of this skill is to create a realistic fixture for testing a gap detector. The new SRS file should be plausible as a real spec, and the code changes should be plausible as real development work. Do not do anything that looks like "I'm trying to create test data for a detector" inside the spec or code — the test data should look like normal, intentional divergence that could happen in real life.