# ADR 0001 - Baseline Path and Product Boundary

## Status
Accepted and in force

## Date
2026-07-28

## Context
The restart effort needs one explicit baseline path so later implementation phases do not reopen earlier planning drift. The reconciled review in [`dist/compiled_update.md`](dist/compiled_update.md) identifies four practical restart priorities:

1. lightweight Python logging for observability
2. a narrow benchmark suite around [`recalculate()`](src/domain/calculations/__init__.py:20)
3. incremental content normalization
4. a single living status surface plus explicit decision records

The same review also identifies an unresolved boundary question between the deterministic rebuild engine and the runtime or gameplay surface. The key code references are:

- [`recalculate()`](src/domain/calculations/__init__.py:20), which is the current live deterministic rebuild pipeline
- [`execute_ability()`](src/application/runtime.py:228), which is the session-oriented ability execution path

This ADR exists to prevent two forms of drift:
- planning drift across multiple markdown artifacts
- implementation drift caused by treating runtime and deterministic-engine concerns as one undifferentiated workstream

## Decision
### 1. Adopt the narrow baseline path for the restart program
The authoritative implementation baseline is:
- lightweight Python logging for observability
- a narrow benchmark suite focused on [`recalculate()`](src/domain/calculations/__init__.py:20)
- incremental content normalization
- separate living status and ADR documents in [`dist/`](dist)

### 2. Treat the deterministic rebuild pipeline as the initial product-stability center
For restart and early implementation phases, the primary stabilization surface is the deterministic engine centered on [`recalculate()`](src/domain/calculations/__init__.py:20).

This means early work should optimize for:
- better insight into rebuild behavior
- confidence in rebuild performance
- safer iteration on content and effect definitions

### 3. Treat runtime and gameplay systems as an adjacent but distinct boundary
The runtime surface centered on [`execute_ability()`](src/application/runtime.py:228) remains part of the product, but it is not the first broad refactor target.

It should be approached as a separate boundary because it introduces:
- event sequencing
- resource spending
- target resolution
- activated effect application
- session-time mutation patterns that are different from pure deterministic rebuild

### 4. Do not declare a new canonical rebuild authority during Phase 0
Phase 0 records current reality. It does not rewrite authority.

Current reality is:
- the live deterministic rebuild flow runs through [`recalculate()`](src/domain/calculations/__init__.py:20)
- runtime systems invoke rebuild after execution through [`execute_ability()`](src/application/runtime.py:307)
- future authority changes require a separate decision after evidence from logging and benchmarking is available

## Rationale
### Why this baseline path
- It is aligned with the authoritative parent-program instruction.
- It avoids opening multiple risky fronts at once.
- It addresses the two most practical restart blockers first: weak observability and lack of performance evidence.

### Why anchor the first work around [`recalculate()`](src/domain/calculations/__init__.py:20)
- The deterministic rebuild path is central to state correctness.
- Existing regression coverage already treats rebuild behavior as a major invariant.
- A narrow benchmark suite is easiest to define around a stable deterministic entrypoint.

### Why keep [`execute_ability()`](src/application/runtime.py:228) in the boundary framing
- Runtime execution is where session behavior becomes user-visible.
- It is a high-risk surface for debugging and future gameplay work.
- It benefits from observability, but it should not force early architecture expansion ahead of the baseline plan.

## Consequences
### Positive
- Restart work gets one unambiguous baseline.
- Implementation can begin without pretending unresolved runtime questions are already settled.
- The program gains a clean split between living status tracking and historical reference material.

### Negative
- Some long-term architecture questions remain deliberately deferred.
- Contributors must tolerate a transitional state where deterministic and runtime concerns still coexist in separate layers.

### Neutral operational rule
If an implementation idea does not directly support lightweight logging, narrow rebuild benchmarking, or incremental content normalization, it should be treated as outside the current baseline until a later decision promotes it.

## Non-goals for this ADR
- selecting the full logging schema
- selecting exact benchmark fixtures
- choosing the first normalization target
- resolving every runtime architecture ambiguity
- broadening the retained [`dist/`](dist) document set beyond the active living surfaces and baseline analysis

## Operational guardrails established by this ADR
1. Logging work remains lightweight and evidence-oriented.
2. Benchmark work stays centered on [`recalculate()`](src/domain/calculations/__init__.py:20).
3. Content normalization begins with an incremental pilot, not a sweeping migration.
4. Any proposal to change canonical rebuild authority or merge runtime and deterministic responsibilities requires a follow-on ADR.

## Relationship to other documents
- Living program status, roadmap, and backlog are tracked in [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md).
- Reconciled repository analysis remains in [`dist/compiled_update.md`](dist/compiled_update.md).
- The retained active [`dist/`](dist) set is intentionally limited to these three documents unless [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) explicitly expands it.

## Follow-on questions for parent-program review
1. Which benchmark fixtures best represent realistic rebuild complexity for [`recalculate()`](src/domain/calculations/__init__.py:20).
2. Which runtime touchpoints beyond [`execute_ability()`](src/application/runtime.py:228) deserve first-pass logging.
3. Which content family should be the first normalization pilot.
4. Whether a later ADR should formalize canonical rebuild authority beyond current live behavior.
