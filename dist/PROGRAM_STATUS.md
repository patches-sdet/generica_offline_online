# Program Status - Authoritative Source of Truth

## Purpose
This document is the living source of truth for the restart program derived from [`dist/compiled_update.md`](dist/compiled_update.md). It now serves as the single maintained roadmap, status, and practical backlog surface for the phased investment program.

## Authority and maintenance rule
- **Authoritative status document:** [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md)
- **Authoritative baseline analysis:** [`dist/compiled_update.md`](dist/compiled_update.md)
- **Authoritative baseline decision record:** [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md)
- **Historical plans and audits:** reference-only unless explicitly reactivated in this document

## Why this location and naming are the lowest-risk option
- [`dist/`](dist) now contains the reduced active body of restart-program artifacts: [`dist/compiled_update.md`](dist/compiled_update.md), [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md), and [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md).
- Keeping the living status file beside the reconciled baseline analysis avoids introducing a new documentation root.
- The filename [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) is explicit, searchable, and unambiguous as the sole status surface.
- The ADR is colocated in [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md) so decision history stays adjacent to the planning materials it governs.

## Program frame
The restart effort is proceeding from the reconciled findings in [`dist/compiled_update.md`](dist/compiled_update.md), not from stale status assumptions in older WBS or audit files. The chosen baseline path is intentionally narrow:

1. lightweight Python logging for observability
2. a narrow benchmark suite around [`recalculate()`](src/domain/calculations/__init__.py:20)
3. incremental content normalization
4. a separate decision log plus this living status document

## Baseline decisions in force
### D-01: Documentation-first Phase 0
Phase 0 produces the documentation foundation before implementation work begins.

### D-02: Deterministic engine is the initial stabilization center
The first implementation phases should center on the deterministic rebuild surface anchored by [`recalculate()`](src/domain/calculations/__init__.py:20), not on broad runtime feature expansion.

### D-03: Runtime and gameplay work remains in scope but behind explicit decision gates
Runtime systems anchored by [`execute_ability()`](src/application/runtime.py:228) are important, but they are not the first surface to expand until baseline observability and performance confidence exist.

### D-04: Planning fragmentation ends here
This file becomes the only actively maintained program-status surface unless it explicitly delegates a subsection to another living file.

## Phase status
| Phase | Status | Scope | Exit condition |
| --- | --- | --- | --- |
| Phase 0 | Complete | Documentation foundation and decision alignment | Living status doc and ADR are in place and approved |
| Phase 1 | Complete | Lightweight observability around deterministic and runtime choke points | Logging scope approved and insertion points confirmed |
| Phase 1.5 | Complete | Repo-wide logging formatter and handler convention for stable JSON-shaped external logs | Logging output convention is wired and consistent with the Phase 1 observability surface |
| Phase 2 | Complete | Narrow benchmark harness around [`recalculate()`](src/domain/calculations/__init__.py:20) | Benchmark command path exists, representative fixtures run reproducibly, an initial local baseline is recorded, and CI publishes non-blocking benchmark artifacts |
| Phase 2.5 | Complete | CI publication for benchmark artifacts | Workflow uploads reproducible benchmark reports without introducing a performance gate |
| Phase 3 | Complete | Incremental content normalization on a low-risk content surface | Conservative Berserker pilot normalization is merged and deferred follow-up candidates are recorded |
| Phase 4 | Complete | Documentation-surface consolidation and repo push-readiness review | Living status, ADR, and contributor entrypoints reflect current state and the retained [`dist/`](dist) set is unambiguous |
| Next candidate | Planned | Execute the next low-risk normalization or adjacent evidence-backed follow-up from the backlog below | Parent program selects the next slice from the recorded backlog |

Phase 1 established lightweight observability around the deterministic rebuild and runtime choke points. Phase 1.5 then added a minimal process-level logging convention so structured traces emitted from that instrumentation surface share a stable external JSON log shape when application-level logging is configured.

Phase 2 now has a repo-integrated local benchmark entrypoint in [`src/tools/recalculate_benchmark.py`](src/tools/recalculate_benchmark.py:1), exposed through [`run.sh`](run.sh:1) as `./run.sh benchmark-recalculate`. The harness stays intentionally narrow around standalone [`recalculate()`](src/domain/calculations/__init__.py:20) execution and currently covers three representative scenarios: a minimal human baseline, a Bear/Berserker/Brewer application-flow fixture, and a heavier Crossbreed multi-progression fixture. CI also runs the same command in [`.github/workflows/test.yml`](.github/workflows/test.yml:1) and uploads a `recalculate-benchmark` artifact containing markdown and JSON outputs for comparison, without applying any performance threshold gate.

Phase 3 completed a tightly scoped Berserker pilot against [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml). The implemented low-risk slice uses the YAML file only for already-established shared grants `Growl`, `Rage`, `Toughness`, and `Fast as Death` while leaving Berserker-unique active and passive implementations on the legacy path in [`src/domain/abilities/adventure/legacy_abilities/berserker.py`](src/domain/abilities/adventure/legacy_abilities/berserker.py:1).

## Living roadmap and backlog
### Completed program record
- **Phase 0:** source-of-truth setup through [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) and [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md)
- **Phase 0 cleanup:** [`dist/`](dist) reduced to the active retained set only
- **Phase 1:** observability implementation across the approved deterministic and runtime choke points
- **Phase 1.5:** repo-wide logging formatter and handler convention for stable external log shape
- **Phase 2:** narrow local benchmark harness around [`recalculate()`](src/domain/calculations/__init__.py:20)
- **Phase 2.5:** CI publication of non-blocking benchmark artifacts
- **Phase 3:** conservative Berserker pilot normalization
- **Phase 4:** living-doc consolidation and push-readiness review

### Deferred normalization candidates
- Additional adventure-job YAML conversions that are limited to clearly shared grant lists and avoid unique runtime behavior
- Other obviously duplicated shared-ability references where the YAML path can express existing behavior without changing authority or sequencing
- Small follow-on cleanup around Berserker documentation and mapping consistency only after another candidate is selected

### Explicitly deferred for now
- Berserker-unique active abilities and passives that still depend on legacy implementations in [`src/domain/abilities/adventure/legacy_abilities/berserker.py`](src/domain/abilities/adventure/legacy_abilities/berserker.py:1)
- Broad runtime architecture changes around [`execute_ability()`](src/application/runtime.py:228)
- Any attempt to promote runtime-layer helpers into new canonical deterministic rebuild authority without a follow-on ADR

### Practical next-candidate backlog
1. Select the next low-risk normalization slice from clearly shared grant lists.
2. Compare benchmark artifact runs over time to watch for meaningful drift before introducing any thresholding discussion.
3. Decide whether any additional lightweight runtime touchpoints merit observability follow-on work without widening scope.
4. Revisit longer-term rebuild-authority questions only after more evidence accumulates from the existing logging and benchmark surfaces.

### Initial local Phase 2 baseline
Current baseline is recorded from the local benchmark harness and is non-blocking by design. It is intended for future comparison only, not as a pass/fail gate.

| Scenario | Cold ms | Warm median ms | Notes |
| --- | ---: | ---: | --- |
| human_baseline | 0.079 | 0.049 | Freshly created single-race character |
| bear_berserker_brewer | 0.144 | 0.116 | Representative [`create_character()`](src/application/character_creation.py:170) + allocations flow |
| crossbreed_multi_progression | 0.145 | 0.140 | Heavier layered rebuild case |

## Current understanding of the product boundary
### Deterministic engine side
The deterministic engine is the rebuild-oriented state derivation path that starts from content and owned character state, then resolves final derived state through [`recalculate()`](src/domain/calculations/__init__.py:20).

This side currently includes:
- registry-backed content bootstrap
- passive and granted ability reconstruction
- effect collection
- attribute, pool, defense, and tag derivation
- regression expectations around deterministic rebuild behavior

### Runtime and gameplay side
The runtime side is the session-oriented, eventful, ability-activation surface centered on [`execute_ability()`](src/application/runtime.py:228), effect application, resource spending, targeting, and event dispatch.

This side currently includes:
- activated ability execution
- effect application ordering
- resource spending at use time
- runtime event emission
- gameplay-session behaviors that may mutate state before deterministic rebuild is re-applied

### Boundary rule for upcoming work
- Phase 1 and Phase 2 may instrument both sides.
- Phase 1 and Phase 2 should not attempt a major boundary rewrite.
- Any attempt to promote runtime rebuild helpers into canonical deterministic authority requires a parent-program decision after benchmark and observability work establish evidence.

## Decisions now in force from completed phases
### D-05: Rebuild authority remains explicitly acknowledged
The current live deterministic rebuild path remains [`recalculate()`](src/domain/calculations/__init__.py:20). Alternative reconstruction logic is not treated as canonical without an explicit follow-on decision.

### D-06: Initial logging targets were intentionally narrow
The first logging surface centered on [`recalculate()`](src/domain/calculations/__init__.py:20), [`collect_effects()`](src/domain/effects/aggregation.py:29), [`execute_ability()`](src/application/runtime.py:228), and [`emit_event()`](src/application/events.py:8).

### D-07: Benchmark scope remains intentionally narrow
The benchmark suite stays centered on representative rebuild scenarios around [`recalculate()`](src/domain/calculations/__init__.py:20), not broad application-wide load testing.

### D-08: Content normalization remains pilot-first
The first normalization slice stayed low risk and incremental rather than opening a generalized refactor.

## Risks
| ID | Risk | Why it matters | Current handling |
| --- | --- | --- | --- |
| R-01 | Documentation drift returns | Old and new plans may diverge again | Maintain status only in [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) |
| R-02 | Runtime ambiguity blocks implementation | Contributors may confuse deterministic authority with runtime helper paths | Use [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md) as governing decision |
| R-03 | Observability grows too wide too early | Broad logging rewrites would slow restart momentum | Limit initial work to lightweight Python logging |
| R-04 | Benchmarking expands beyond the narrow goal | Large performance programs would delay confidence-building | Benchmark only representative [`recalculate()`](src/domain/calculations/__init__.py:20) flows first |
| R-05 | Content normalization reopens architecture debates prematurely | Normalization touches content-model assumptions | Keep it incremental and evidence-based |

## Push-readiness review
### Safe Phase 4 findings
- The retained [`dist/`](dist) surface is already minimal and unambiguous: [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md), [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md), and [`dist/compiled_update.md`](dist/compiled_update.md).
- The main documentation drift found during Phase 4 was wording that still read like an unaccepted proposal or referenced removed status artifacts.
- [`README.md`](README.md) contained a stale link to a removed [`dist/code_audit.md`](dist/code_audit.md) surface and restart guidance that needed to point contributors to the retained living documents instead.

### Remaining manual checks before push
1. Review the final `git diff` to confirm only the intended documentation-surface changes are included.
2. Verify there are no untracked local artifacts that should stay out of the push.
3. Confirm benchmark artifacts, caches, and local environment files remain excluded from the commit.
4. If desired, run the standard test and benchmark commands once more before push for operator confidence, even though Phase 4 itself is documentation-only.

## Active document set
### Actively maintained
- [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md)
- [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md)
- [`dist/compiled_update.md`](dist/compiled_update.md) as the reconciled baseline analysis for this restart effort

### Removed during Phase 0 cleanup
- Legacy WBS, audit, charter, implementation-plan, and helper-note artifacts that were superseded by [`dist/compiled_update.md`](dist/compiled_update.md), [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md), and [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md) have been deleted to keep the top-level [`dist/`](dist) surface small and unambiguous.

## Open issues requiring parent-program consultation
1. Whether the longer-term canonical ability rebuild authority should remain the live deterministic hook in [`src/domain/calculations/abilities.py`](src/domain/calculations/abilities.py:4) or eventually migrate toward runtime-layer helpers after explicit validation.
2. Which concrete content family is the safest next normalization candidate after the Berserker pilot.
3. Whether benchmark comparison should remain artifact-only or eventually add light policy around acceptable drift.
4. Whether any additional runtime instrumentation is warranted beyond the deliberately narrow Phase 1 surface.
