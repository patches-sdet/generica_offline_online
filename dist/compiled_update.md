## Executive Summary
This audit reviewed the full Python project with special reconciliation against historical artifacts in [`dist/`](dist), especially [`dist/code_audit.md`](dist/code_audit.md), [`dist/audit_summary.md`](dist/audit_summary.md), [`dist/PROJECT_CHARTER.md`](dist/PROJECT_CHARTER.md), and [`dist/WBS_REMAINING.md`](dist/WBS_REMAINING.md). The codebase still has a strong deterministic-engine core centered on [`recalculate()`](src/domain/calculations/__init__.py:18), registry bootstrap in [`initialize_content_registries()`](src/domain/content_registry.py:257), and a reasonably organized test suite, but it remains in a transitional state: runtime/progression features are partially stabilized, test architecture is ahead of actual implementation in some areas, and project-management artifacts in [`dist/`](dist) overstate some gaps that code now partially addresses.

Most important for restarting after a long break: CI is present now in [`.github/workflows/test.yml`](.github/workflows/test.yml), registry helper deduplication already landed in [`_get_from_registry()`](src/domain/content_registry.py:31), but the project still carries unresolved technical direction around runtime execution, dual ability modeling, incomplete observability, and documentation drift between [`README.md`](README.md), [`tests/test_plan.md`](tests/test_plan.md), and the live code.

## Key Findings
1. **The architectural core is sound, but major subsystems are still explicitly transitional.** Evidence includes transitional comments on [`Character.abilities`](src/domain/character.py:94), merge-rule comments in [`rebuild_abilities()`](src/application/runtime.py:321), and roadmap/TODO markers in [`README.md`](README.md) and [`level_profession_job()`](src/application/leveling.py:311). Impact: maintainability and decision latency are higher than raw test count suggests.

2. **Historical audit conclusions in [`dist/code_audit.md`](dist/code_audit.md) are partly stale.** Two major prior “quick wins” have already been implemented: generic registry helpers exist in [`src/domain/content_registry.py`](src/domain/content_registry.py), and CI exists in [`.github/workflows/test.yml`](.github/workflows/test.yml). However, the remaining concerns about runtime-test incompleteness, ability-model overlap, and observability are still valid.

3. **Testing is materially stronger than the documentation implies, but still skewed toward unit/regression coverage and away from realistic workflow coverage.** The live suite includes smoke, regression, blackbox, application, calculations, effects, runtime, content, and skills tests under [`tests/`](tests), yet the strategic plan in [`tests/test_plan.md`](tests/test_plan.md) still describes an intended future structure larger than what exists. Impact: decent change safety for known rules, weaker safety for end-to-end user flows and runtime interactions.

4. **Runtime/progression behavior is partially tested but not fully stabilized.** Runtime awards are exercised in files like [`tests/unit/runtime/test_experience_die_awards.py`](tests/unit/runtime/test_experience_die_awards.py), but placeholders remain in [`tests/unit/runtime/test_resource_spend_placeholder.py`](tests/unit/runtime/test_resource_spend_placeholder.py) and [`tests/unit/runtime/test_toughness_progression_placeholder.py`](tests/unit/runtime/test_toughness_progression_placeholder.py). Impact: the highest-risk “gameplay session” behaviors are still the least trustable.

5. **Developer experience is workable but brittle.** The repo has a runnable entrypoint in [`run.sh`](run.sh), test instructions in [`tests/README.md`](tests/README.md), and an interactive bootstrap in [`src/startup.py`](src/startup.py), but setup/documentation are inconsistent: [`README.md`](README.md) references commands and files that do not match the current package layout, and many workflows rely on ad hoc prints rather than structured diagnostics. Impact: slower re-onboarding and more manual debugging after a long break.

## Supporting Observations

### Test Coverage & Strategy
- Exact coverage was **not executed**, so all coverage assessments are from file inspection only.
- Test organization is stronger than the older reports suggest. Current directories include [`tests/smoke/`](tests/smoke), [`tests/regression/`](tests/regression), [`tests/blackbox/`](tests/blackbox), [`tests/unit/application/`](tests/unit/application), [`tests/unit/calculations/`](tests/unit/calculations), [`tests/unit/content/`](tests/unit/content), [`tests/unit/effects/`](tests/unit/effects), [`tests/unit/runtime/`](tests/unit/runtime), and [`tests/unit/skills/`](tests/unit/skills).
- The suite clearly protects critical invariants around deterministic rebuild and registry bootstrap, especially in [`tests/regression/test_deterministic_rebuild.py`](tests/regression/test_deterministic_rebuild.py), [`tests/regression/test_no_duplicate_registration_on_force_reload.py`](tests/regression/test_no_duplicate_registration_on_force_reload.py), [`tests/smoke/test_bootstrap.py`](tests/smoke/test_bootstrap.py), and [`tests/unit/content/test_registry_bootstrap.py`](tests/unit/content/test_registry_bootstrap.py).
- Blackbox coverage exists but is narrow. [`tests/blackbox/test_shared_ability_stacking.py`](tests/blackbox/test_shared_ability_stacking.py) and [`tests/blackbox/test_shared_healing_stack.py`](tests/blackbox/test_shared_healing_stack.py) validate outcome behavior, but there is little evidence of broader character-lifecycle blackbox coverage.
- The intended strategy in [`tests/test_plan.md`](tests/test_plan.md) is stronger than the implemented strategy. That file proposes integration and E2E layers, but those layers do not appear as first-class implemented suites.
- Estimated state: **good coverage of deterministic recalculation and progression rules, moderate coverage of runtime stat/skill awards, weak coverage of ability execution/resource spending/CLI workflows, and no verified performance coverage**.

### Test Quality
- Tests are generally readable, specific, and named well, for example [`test_recalculate_is_idempotent_for_same_inputs`](tests/regression/test_deterministic_rebuild.py:39) and [`test_level_adventure_job_spends_points_and_increments_progression`](tests/unit/application/test_adventure_leveling.py:80).
- Fixtures are simple and reliable. [`initialized_content`](tests/conftest.py:27) resets and reloads registries conservatively, which is good for isolation but may hide performance issues and encourage expensive full-bootstrap patterns.
- Builder support is minimal. [`tests/helpers/builders.py`](tests/helpers/builders.py) only provides a few helpers, and assertions are similarly sparse in [`tests/helpers/assertions.py`](tests/helpers/assertions.py). That makes many tests repetitive and encourages direct low-level setup.
- Runtime placeholders are still a real quality signal, not just bookkeeping noise. The skips in [`tests/unit/runtime/test_resource_spend_placeholder.py`](tests/unit/runtime/test_resource_spend_placeholder.py) and [`tests/unit/runtime/test_toughness_progression_placeholder.py`](tests/unit/runtime/test_toughness_progression_placeholder.py) correspond to exactly the areas the code comments still frame as unsettled.
- A subtle quality risk: some tests validate internals against transitional behavior rather than stable product semantics, especially around ability-level reconstruction and progression rules.

### CI/CD & Automation
- Contrary to older audit artifacts, CI exists. [`.github/workflows/test.yml`](.github/workflows/test.yml) runs on push and pull request, uses a Python version matrix, installs [`pytest`](pyproject.toml) and coverage tooling, runs [`pytest`](pytest.ini), and enforces `coverage report --fail-under=70`.
- That means the “no CI/CD configuration found” claim in [`dist/code_audit.md`](dist/code_audit.md) and the “not started” status in [`dist/WBS_REMAINING.md`](dist/WBS_REMAINING.md) are outdated.
- CI is still basic. There is no evidence of linting, formatting, type checking, dependency caching, artifact publishing, release automation, flaky-test quarantine, or benchmark jobs.
- Dependency automation is minimal. [`pyproject.toml`](pyproject.toml) only declares project metadata and a script entrypoint; it does not define dependencies, optional groups, tooling configuration, or test extras.
- Local automation is thin but present. [`run.sh`](run.sh) provides a default app launcher and job-generation helpers, but there is no dedicated test runner, no Makefile, and no unified developer bootstrap.

### Developer Experience
- Re-entry points exist: [`run.sh`](run.sh), [`src/main.py`](src/main.py), [`src/cli.py`](src/cli.py), and [`src/startup.py`](src/startup.py).
- The interactive bootstrap in [`src/startup.py`](src/startup.py) is particularly useful for restarting work because it exposes registry inspection, progression probes, and a full audit helper like [`run_full_job_ability_audit()`](src/startup.py:205).
- However, README drift is significant. [`README.md`](README.md) still tells users to run `pip install -r requirements.txt` and `python main.py`, but the visible repo root does not include a [`requirements.txt`](requirements.txt) file and the actual entrypoint is more consistent with [`src/main.py`](src/main.py) or [`run.sh`](run.sh).
- Project docs also disagree on maturity. [`README.md`](README.md) presents a broad architecture/roadmap, [`tests/README.md`](tests/README.md) frames the test tree as a scaffold replacing older tests, and [`dist/WBS_COMPLETED.md`](dist/WBS_COMPLETED.md) / [`dist/WBS_REMAINING.md`](dist/WBS_REMAINING.md) present PM-style status tracking that no longer matches live code in several areas.
- The CLI is usable but large and monolithic. [`src/cli.py`](src/cli.py) contains bootstrapping, prompts, allocation flows, save/load behavior, ability use, and leveling menus in one file, which raises onboarding and maintenance cost.

### Observability & Debugging
- There is very little structured observability. Search inspection shows widespread `print(...)`-based messaging in [`src/cli.py`](src/cli.py), [`src/application/leveling.py`](src/application/leveling.py), [`src/startup.py`](src/startup.py), and [`src/presentation/character_sheet.py`](src/presentation/character_sheet.py), but no meaningful use of the standard [`logging`](rules.md) framework.
- The engine does have some internal debug-friendly state. [`Character._attribute_sources`](src/domain/character.py:49), [`Character.manual_attribute_increases`](src/domain/character.py:40), and bootstrap probes in [`src/startup.py`](src/startup.py) are helpful for manual diagnosis.
- Runtime event handling is minimal and opaque. [`emit_event()`](src/application/events.py:8) dispatches listeners with no logging, no return structure, no failure aggregation, and no listener registry scoping.
- Ability execution has some failure surfacing via [`apply_effects()`](src/application/runtime.py:162), which emits `effect_failed`, but there is no persistent trace, structured error payload, or audit log.
- For a project resuming after a long pause, observability is one of the largest practical blockers: the code can often be inspected, but failures during gameplay flows will still require stepping through code rather than reading useful diagnostics.

## Risk Areas
1. **Ability state model and rebuild path** — [`Character`](src/domain/character.py) still carries [`abilities`](src/domain/character.py:95), [`ability_levels`](src/domain/character.py:98), and [`ability_provenance`](src/domain/character.py:101). The live rebuild path in [`src/domain/calculations/abilities.py`](src/domain/calculations/abilities.py) coexists with another [`rebuild_abilities()`](src/application/runtime.py:275), which is a strong signal of conceptual overlap and potential drift.

2. **Runtime execution and event-driven mechanics** — [`execute_ability()`](src/application/runtime.py:186), [`emit_event()`](src/application/events.py:8), and skipped runtime placeholders in [`tests/unit/runtime/`](tests/unit/runtime) indicate that the most dynamic gameplay behavior remains the least settled. Failures here are likely to be subtle and user-visible.

3. **Documentation and status drift** — [`README.md`](README.md), [`tests/test_plan.md`](tests/test_plan.md), and multiple artifacts in [`dist/`](dist) disagree with the live state of CI, packaging, and roadmap. This increases restart friction and raises the risk of solving already-solved problems or trusting outdated recommendations.

4. **Developer bootstrap and dependency definition** — [`pyproject.toml`](pyproject.toml) is too sparse to serve as a reliable project contract. Missing dependency declarations and incomplete tool configuration increase environment recreation risk after a long break.

5. **Monolithic CLI and user-flow coupling** — [`src/cli.py`](src/cli.py) centralizes too many concerns, making it a likely hotspot for regressions and a poor boundary for isolated testing.

6. **Observability gap in core workflows** — Lack of structured logs around registry initialization, effect aggregation in [`collect_effects()`](src/domain/effects/aggregation.py:29), and runtime execution means future bugs will be expensive to localize.

## Recommended Actions

### Quick Wins
- **Update onboarding docs to match reality.** Reconcile [`README.md`](README.md), [`tests/README.md`](tests/README.md), and the current entrypoints in [`run.sh`](run.sh), [`src/main.py`](src/main.py), and [`.github/workflows/test.yml`](.github/workflows/test.yml).
- **Treat [`dist/`](dist) as historical context only and explicitly mark stale items.** At minimum, note that CI and registry-helper work are already complete compared with [`dist/code_audit.md`](dist/code_audit.md) and [`dist/WBS_REMAINING.md`](dist/WBS_REMAINING.md).
- **Replace the two runtime placeholders first.** The skipped tests in [`tests/unit/runtime/test_resource_spend_placeholder.py`](tests/unit/runtime/test_resource_spend_placeholder.py) and [`tests/unit/runtime/test_toughness_progression_placeholder.py`](tests/unit/runtime/test_toughness_progression_placeholder.py) are the clearest high-value gap.
- **Document the authoritative rebuild path.** Clarify whether [`rebuild_abilities()`](src/domain/calculations/abilities.py:3) or [`rebuild_abilities()`](src/application/runtime.py:275) is canonical, and whether the latter should exist at all.
- **Add one restart-oriented “known good workflow” doc.** A short note pointing to [`initialize_content_registries()`](src/domain/content_registry.py:257), [`create_character()`](src/application/character_creation.py:170), [`recalculate()`](src/domain/calculations/__init__.py:18), and [`run_full_job_ability_audit()`](src/startup.py:205) would pay off immediately.

### Medium-term Improvements
- **Consolidate ability modeling.** Finish the transition around [`ability_provenance`](src/domain/character.py:101) versus derived executable ability levels. Historical guidance in [`dist/provenance_guide.md`](dist/provenance_guide.md) and [`dist/leveled_skills.md`](dist/leveled_skills.md) is still relevant here.
- **Introduce integration tests for real workflows.** Prioritize character creation → progression → recalculation, and active ability execution with resource spend. The intent already exists in [`tests/test_plan.md`](tests/test_plan.md).
- **Refactor [`src/cli.py`](src/cli.py) into smaller testable units.** Separate prompt/UI logic from domain/application actions.
- **Improve packaging/tooling in [`pyproject.toml`](pyproject.toml).** Define dependencies, test extras, tool configs, and possibly a documented install path instead of relying on implicit environment state.
- **Expand shared test fixtures.** Grow [`tests/helpers/builders.py`](tests/helpers/builders.py) and [`tests/helpers/assertions.py`](tests/helpers/assertions.py) to reduce duplication and enable more realistic test setup.

### Long-term Investments
- **Formalize observability and debugging.** Replace ad hoc prints with structured logging and add trace points around [`collect_effects()`](src/domain/effects/aggregation.py:29), [`execute_ability()`](src/application/runtime.py:186), and registry bootstrap in [`initialize_content_registries()`](src/domain/content_registry.py:257).
- **Benchmark the deterministic pipeline.** The charter target in [`dist/PROJECT_CHARTER.md`](dist/PROJECT_CHARTER.md) calls for sub-100ms recalculation, but there is no verified benchmark suite.
- **Continue data-driven content normalization carefully.** Historical artifacts like [`dist/job_builder_help.md`](dist/job_builder_help.md), [`dist/shared_ability_help.md`](dist/shared_ability_help.md), and [`dist/checklist_audit.md`](dist/checklist_audit.md) still support the case for reducing content-authoring duplication once the substrate is stable.
- **Establish a single source of project truth.** The combination of [`dist/WBS_COMPLETED.md`](dist/WBS_COMPLETED.md), [`dist/WBS_REMAINING.md`](dist/WBS_REMAINING.md), and multiple design notes suggests planning fragmentation. Pick one living status surface.

### Suggested Tools & Patterns
- Use Python `logging` in place of `print(...)` for engine/runtime internals, while keeping CLI presentation in [`src/cli.py`](src/cli.py) user-facing.
- Add [`pytest-cov`](.github/workflows/test.yml) output artifacts in CI so coverage trends are visible, not only threshold-gated.
- Consider a small “golden workflow” fixture layer built on [`create_character()`](src/application/character_creation.py:170) and [`recalculate()`](src/domain/calculations/__init__.py:18) for integration tests.
- Add snapshot-style assertions for visible state similar to [`snapshot()`](tests/regression/test_deterministic_rebuild.py:7) but promoted into shared helpers.
- If runtime systems stay in scope, add explicit event/debug traces around [`emit_event()`](src/application/events.py:8) and effect application in [`apply_effects()`](src/application/runtime.py:162).

## Restart Guide / Catch-up Notes
1. **Start with the live engine, not the historical reports.** Use [`src/startup.py`](src/startup.py), [`src/application/character_creation.py`](src/application/character_creation.py), [`src/domain/calculations/__init__.py`](src/domain/calculations/__init__.py), and [`src/domain/content_registry.py`](src/domain/content_registry.py) as current truth.
2. **Use [`dist/code_audit.md`](dist/code_audit.md) and [`dist/audit_summary.md`](dist/audit_summary.md) only as context.** They still help explain prior concerns, but they are outdated on CI and registry-helper status.
3. **Reconfirm the intended boundary between “core deterministic engine” and “runtime/gameplay systems.”** Historical context in [`dist/scope_creep_audit.md`](dist/scope_creep_audit.md) and [`dist/PROJECT_CHARTER.md`](dist/PROJECT_CHARTER.md) shows this was a major unresolved direction question.
4. **First practical verification pass after returning:** inspect [`.github/workflows/test.yml`](.github/workflows/test.yml), then run the smoke/regression/runtime suites described in [`tests/README.md`](tests/README.md), and use [`run_full_job_ability_audit()`](src/startup.py:205) from [`src/startup.py`](src/startup.py) for content sanity.
5. **First implementation targets after the audit:** replace skipped runtime tests, reconcile docs, and decide the canonical ability model before making new gameplay changes.

Audit completed as a no-modification repository review with explicit reconciliation against historical artifacts in [`dist/`](dist); no runtime metrics or coverage numbers were executed, so all quantitative statements beyond file counts and visible configuration are inspection-based estimates only.