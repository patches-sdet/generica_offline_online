# Generica Offline Online — Test Plan

This document defines a practical, architecture-aligned testing strategy for the current engine.

It is designed to cover four complementary layers:

- smoke tests
- black-box tests
- regression tests
- unit tests

The goal is to protect the current deterministic, registry-driven engine while keeping the test suite fast enough to run often during refactors.

---

## 1. Testing Goals

The current engine has several core invariants that should drive the test design:

1. **Deterministic rebuild**
   - `state = function(all inputs)`
   - repeated recalculation should not drift state

2. **Registry-first content resolution**
   - content is loaded into canonical registries
   - progressions grant abilities through the registry, not by storing content objects on the character

3. **Effects are the only mutation mechanism for rebuild-derived state**
   - ability outputs must normalize to flat effect lists

4. **Shared abilities must register once and grant from many sources**
   - example: `Growl`, `Quickdraw`, `Fast as Death`

5. **Pipeline ordering matters**
   - reset derived
   - rebuild abilities
   - rebuild skills
   - collect effects
   - rebuild attributes
   - apply derived effects
   - calculate pools
   - calculate defenses
   - rebuild tags

6. **Runtime behavior must remain separable from rebuild behavior**
   - runtime triggers should not break deterministic recalculate
   - rebuild-safe passives should not depend on event-only context

---

## 2. Recommended Test Suite Structure

Replace the current legacy-oriented test layout with a structure that mirrors the engine architecture.

```text
tests/
  conftest.py
  helpers/
    registry.py
    characters.py
    assertions.py
  smoke/
    test_bootstrap.py
    test_registry_load.py
    test_shared_abilities.py
    test_recalculate_smoke.py
  blackbox/
    test_character_builds.py
    test_cli_flows.py
    test_progression_composition.py
    test_runtime_ability_use.py
  regression/
    test_deterministic_rebuild.py
    test_no_stat_drift.py
    test_shared_ability_reload.py
    test_duplicate_ability_stacking.py
    test_derived_ordering.py
    test_pool_bonus_rules.py
    test_material_race_behavior.py
  unit/
    abilities/
      test_build_ability.py
      test_patterns.py
      test_shared_ability_builder.py
    calculations/
      test_rebuild_abilities.py
      test_attributes.py
      test_derived.py
      test_pools.py
      test_defenses.py
      test_tags.py
    effects/
      test_aggregation.py
      test_stat_effects.py
      test_conditional.py
      test_scaling.py
      test_resource_effects.py
      test_special_attack.py
      test_special_roll.py
      test_special_state.py
      test_special_tag.py
    registry/
      test_content_registry.py
      test_module_reload.py
      test_progression_ability_grants.py
    runtime/
      test_execute_ability.py
      test_resource_spend.py
      test_target_resolution.py
    content/
      test_adventure_jobs.py
      test_professions.py
      test_races.py
      test_advanced_jobs.py
      test_shared_content.py
```

This keeps tests aligned with the codebase instead of the old monolithic model.

---

## 3. Test Categories

### 3.1 Smoke Tests

Smoke tests should answer one question:

**Can the engine boot and perform its most important end-to-end actions without crashing?**

These should be very small in number, very fast, and run constantly.

#### Recommended smoke tests

##### `smoke/test_bootstrap.py`
- `initialize_content_registries(force=True)` completes without exception
- all major registries are non-empty afterward
- no duplicate registration crash occurs during reload

##### `smoke/test_registry_load.py`
- key content exists after bootstrap
- examples:
  - `has_ability("Growl")`
  - `has_ability("Quickdraw")`
  - `has_ability("Fast as Death")`
  - `get_progression_ability_grants("race", "Bear")`
  - `get_progression_ability_grants("adventure", "Berserker")`

##### `smoke/test_shared_abilities.py`
- shared ability registers once
- Bear + Berserker grants `Growl`
- duplicate stacking yields effective level 6

##### `smoke/test_recalculate_smoke.py`
- create a minimal valid character
- assign a race and one adventure progression
- run `recalculate(character)`
- assert that:
  - attributes are populated
  - pools are populated
  - defenses are populated
  - no crash occurs from passive/shared abilities

These should run on every test invocation.

---

### 3.2 Black-Box Tests

Black-box tests should treat the engine as an external user would:

- construct characters
- level or assign progressions
- use abilities
- inspect final visible state

These tests should avoid asserting too much about internals like intermediate effect lists.

#### Recommended black-box tests

##### `blackbox/test_character_builds.py`
Build representative characters and assert visible outcomes:

- Bear Berserker gets `Growl` at level 6
- Cleric Oracle gets `Lesser Healing` stacked correctly
- Orc + Leather Toy Golem defense totals reflect additive bonuses
- template/base race composition behaves correctly

##### `blackbox/test_progression_composition.py`
- race + adventure + profession composition rebuilds cleanly
- cross-progression granted abilities unlock at expected levels
- duplicate grants increase by +5 per duplicate source where applicable

##### `blackbox/test_runtime_ability_use.py`
- using an active ability spends the expected pool
- resource-spend failures raise cleanly
- abilities with targets resolve into visible outcome changes

##### `blackbox/test_cli_flows.py`
Only a few high-value flows are needed:

- create a character from CLI helper path
- rebuild character state
- save and exit without crash

If CLI tests become brittle, keep them minimal and focus on application-layer black-box coverage instead.

---

### 3.3 Regression Tests

Regression tests should be created whenever a real bug is fixed.

This project already has several known classes of regressions worth preserving.

#### Recommended regression tests

##### `regression/test_deterministic_rebuild.py`
- recalculating twice produces identical visible state
- recalculating many times does not drift values

##### `regression/test_no_stat_drift.py`
- attributes, pools, defenses, and tags remain stable across repeated rebuilds

##### `regression/test_shared_ability_reload.py`
Protect the recent registry fix:

- `initialize_content_registries(force=True)`
- verify `Growl` exists
- verify Bear/Berserker grants exist
- verify repeated forced reloads do not lose shared content

##### `regression/test_duplicate_ability_stacking.py`
Protect the shared-ability / duplicate-source rule:

- same ability from two sources
- only one logical ability instance
- effective level is `1 + (count - 1) * 5`

##### `regression/test_derived_ordering.py`
Protect the Faith / Fate class of bugs:

- passive derived bonuses from abilities must be present before final defenses are computed
- example: Cleric `Faith` modifies `Fate` correctly after rebuild

##### `regression/test_pool_bonus_rules.py`
Protect the new pool-bonus expansion point:

- Toughness rank increases max HP by `2 * rank`
- characters without Toughness are unaffected
- future pool bonuses can be layered without breaking baseline formulas

##### `regression/test_material_race_behavior.py`
Protect race/template composition bugs:

- base race bonuses survive material template composition
- bonuses stack instead of being silently overridden when intended

##### `regression/test_runtime_rebuild_separation.py`
Protect the Toughness-style bug class:

- passive rebuild generators must not depend on runtime-only event fields
- recalculate on a clean character must never require combat-event context

---

### 3.4 Unit Tests

Unit tests should cover narrow contracts with minimal fixture setup.

These are the tests that let you refactor aggressively.

---

## 4. High-Value Unit Test Targets

### 4.1 Registry and Loader

#### `unit/registry/test_content_registry.py`
Test:
- `register_ability()` rejects duplicates
- `register_progression_ability_grant()` rejects unknown abilities
- grant registration normalizes required level
- grants do not duplicate identical entries

#### `unit/registry/test_module_reload.py`
Test:
- `clear_content_registries()` clears registries
- `clear_content_registries()` removes ability content modules from `sys.modules`
- `initialize_content_registries(force=True)` repopulates shared abilities and grants

#### `unit/registry/test_progression_ability_grants.py`
Test:
- exact grants returned for representative race/adventure/profession combinations
- no phantom grants

---

### 4.2 Ability Builders

#### `unit/abilities/test_build_ability.py`
Test:
- passive definitions create `effect_generator`
- active and skill definitions create `execute`
- missing `effects` raises `ValueError`
- invalid `type` raises `ValueError`
- unlock logic defaults correctly from source type + required level

#### `unit/abilities/test_shared_ability_builder.py`
Test:
- `build_shared_ability()` can register a shared ability
- shared ability default unlock is always true unless overridden
- builder does not double-register on a single build call

#### `unit/abilities/test_patterns.py`
Test pattern contracts independently:
- `scaled_stat_buff`
- `scaled_derived_buff`
- `conditional_effect`
- `skill_check`
- `modify_next_attack`
- `on_event`

Most important assertion: pattern helpers return rebuild-safe or runtime-safe structures as intended.

---

### 4.3 Effect System

#### `unit/effects/test_aggregation.py`
Test:
- `collect_effects()` includes race, progression, passive ability, and runtime effects
- nested results are flattened correctly
- invalid nested/non-effect outputs raise cleanly

#### `unit/effects/test_stat_effects.py`
Test atomic effects:
- `StatIncrease`
- `MultiStatIncrease`
- `DerivedStatBonus`
- `DerivedStatOverride`

#### `unit/effects/test_conditional.py`
Test:
- `ConditionalEffect` applies only when condition passes
- context/target handling is correct

#### `unit/effects/test_scaling.py`
Test:
- scaling wrappers compute correct amounts from level/stat functions

#### `unit/effects/test_resource_effects.py`
Test:
- spend/resource effects mutate pools correctly in runtime contexts
- insufficient resources fail cleanly

#### `unit/effects/test_special_*`
For `attack`, `roll`, `state`, `tag`, `event`:
- each effect mutates only its intended subsystem
- no hidden side effects

---

### 4.4 Calculation Pipeline

#### `unit/calculations/test_rebuild_abilities.py`
Test:
- abilities resolve from progressions via grants
- duplicate-source stacking rule works
- unlock conditions are honored
- non-leveled duplicates do not incorrectly stack

#### `unit/calculations/test_attributes.py`
Test:
- base attributes reset correctly
- source-aware attribute breakdown is correct
- progression/race effects apply once and only once

#### `unit/calculations/test_derived.py`
Test:
- derived bonuses and overrides are applied in correct order
- overrides dominate bonuses where intended

#### `unit/calculations/test_pools.py`
Test:
- baseline formulas from `STAT_FORMULAS` work
- pool bonus hook works
- Toughness affects only HP
- absent pool-bonus abilities default to zero impact

#### `unit/calculations/test_defenses.py`
Test:
- defense totals respect aggregated derived bonuses/overrides
- material/template examples behave correctly

#### `unit/calculations/test_tags.py`
Test:
- tag rebuild clears and reapplies tags deterministically
- shared and progression tags compose correctly

---

### 4.5 Runtime and Application

#### `unit/runtime/test_execute_ability.py`
Test:
- executing a valid ability resolves targets, spends cost, and returns normalized effects
- missing ability raises cleanly

#### `unit/runtime/test_resource_spend.py`
Test:
- pool spend works across all supported pools
- exact-zero and insufficient-resource edge cases

#### `unit/runtime/test_target_resolution.py`
Test:
- self, ally, enemy, and explicit-target flows

#### `unit/runtime/test_event_listeners.py`
As event-driven mechanics grow:
- listeners register/unregister correctly
- runtime events do not pollute deterministic rebuild state

---

## 5. Content Contract Tests

These are especially valuable for a content-heavy engine.

The point is not to test every single skill deeply, but to ensure content modules obey the schema.

### `unit/content/test_adventure_jobs.py`
For each module under `domain/abilities/definitions`:
- imports cleanly
- registers abilities/grants without exception
- every defined ability has required keys
- grant-only entries point to known abilities

### `unit/content/test_professions.py`
Same contract for profession content.

### `unit/content/test_races.py`
Same contract for race content.

### `unit/content/test_advanced_jobs.py`
Same contract for advanced content.

### `unit/content/test_shared_content.py`
Same contract for shared abilities.

These contract tests are often the best way to catch malformed content during rapid authoring.

---

## 6. Fixtures and Helpers

A good test suite here will depend heavily on reusable helpers.

### Recommended helpers

#### `tests/helpers/registry.py`
Utilities:
- `fresh_registries()`
- `bootstrap_content(force=True)`
- `assert_registered_ability(name)`

#### `tests/helpers/characters.py`
Factories:
- `make_blank_character()`
- `make_character_with_progressions(...)`
- `make_bear_berserker()`
- `make_cleric_oracle()`
- `make_orc_toy_golem()`

#### `tests/helpers/assertions.py`
Utilities:
- `assert_recalculate_is_idempotent(character)`
- `assert_same_visible_state(a, b)`
- `assert_has_ability_level(character, ability, level)`

### Fixture guidelines

Prefer fixtures that build **canonical, minimal** characters:

- one blank character
- one race-only character
- one race + adventure character
- one fully composed character

Keep fixtures deterministic and avoid hidden randomness unless the test is specifically about rolling.

---

## 7. Suggested Pytest Markers

Add markers so you can run the suite by confidence level and speed.

```toml
smoke
blackbox
regression
unit
content
slow
runtime
```

Examples:

- `pytest -m smoke`
- `pytest -m "unit and not slow"`
- `pytest -m regression`

---

## 8. Recommended Smoke Matrix

These are the minimum checks worth running frequently.

### Per save / rapid local check
- smoke bootstrap
- smoke shared ability registration
- smoke recalculate
- regression no-stat-drift

### Before merging a refactor
- all smoke
- all unit
- regression shared-ability reload
- regression deterministic rebuild
- black-box representative characters

### Before adding lots of new content
- content contract tests
- smoke bootstrap
- black-box representative build tests

---

## 9. Suggested Initial High-Priority Tests

Build these first, in roughly this order:

1. `smoke/test_bootstrap.py`
2. `smoke/test_shared_abilities.py`
3. `regression/test_shared_ability_reload.py`
4. `regression/test_duplicate_ability_stacking.py`
5. `regression/test_derived_ordering.py`
6. `unit/calculations/test_pools.py`
7. `unit/registry/test_module_reload.py`
8. `unit/effects/test_aggregation.py`
9. `blackbox/test_character_builds.py`
10. `content/test_shared_content.py`

That set protects the most recent and most architecture-sensitive work first.

---

## 10. Example Test Harness Ideas

### Harness A — bootstrap harness
Purpose:
- confirm the engine can fully clear, reload, and register content

Checks:
- forced registry reload succeeds
- representative abilities exist
- representative grants exist

### Harness B — canonical character harness
Purpose:
- generate a small library of known-good characters used by many tests

Examples:
- Bear Berserker
- Cleric Oracle
- Orc Leather Toy Golem
- Elf Bard

Checks:
- visible stats, abilities, tags, and pools are plausible and stable

### Harness C — deterministic rebuild harness
Purpose:
- detect drift instantly

Checks:
- run `recalculate()` N times
- snapshot visible state each pass
- assert all passes are identical

### Harness D — content contract harness
Purpose:
- validate every content module against the builder schema

Checks:
- imports cleanly
- no malformed definitions
- no unknown grant targets
- no duplicate registered abilities unless explicitly shared and centrally defined

### Harness E — runtime separation harness
Purpose:
- ensure deterministic rebuild does not accidentally depend on combat-event state

Checks:
- rebuild a clean character with all passive/shared abilities loaded
- assert no passive generator requires runtime-only fields like `damage_taken`

---

## 11. Suggested Pruning and Cleanup

Based on the current tree, several items are candidates for cleanup or consolidation.

### Safe to prune from repo tracking
These should generally not be committed:

- all `__pycache__/`
- all `*.pyc`

Add or confirm `.gitignore` coverage for them.

### Good candidates for removal or archival
Old artifacts that likely no longer belong in the active code path:

- `src/domain/abilities/builders/_progression_builder.py.old`
- `src/domain/abilities/definitions/_template.py.old`
- `src/domain/abilities/registry.py.old`
- `src/domain/calculations/calculations.py.old`
- `src/domain/effects/effects.py.old`

If you want to keep them, move them to a dedicated `archive/` or `notes/legacy/` folder outside the live package tree.

### Current tests to rename or relocate
These should be converted into the new architecture-aligned structure:

- `tests/unit/duplicate_ability_stacking.py` → `tests/regression/test_duplicate_ability_stacking.py`
- `tests/unit/resource_spend.py` → `tests/unit/runtime/test_resource_spend.py`
- `tests/integration/test_recalculation_pipeline.py` → likely `tests/blackbox/test_character_builds.py` or `tests/regression/test_deterministic_rebuild.py`
- `tests/integration/test_material_races.py` → `tests/regression/test_material_race_behavior.py`

### Root-level utility review
Consider whether these still belong at repo root:

- `check_unbalanced.py`

If still useful, move it under:

```text
tools/
scripts/
```

so the root stays focused.

---

## 12. Recommended Migration Strategy

1. Keep the current tests temporarily.
2. Add the new smoke and regression harnesses first.
3. Port the highest-value existing tests into the new structure.
4. Delete or archive legacy test files only after equivalent coverage exists.
5. Add content contract tests before large new content authoring bursts.

This minimizes coverage gaps while the architecture continues to settle.

---

## 13. Definition of Done for the Test Suite

A strong baseline for the current project state would be:

- smoke tests all passing
- deterministic rebuild regression tests passing
- shared-ability reload regression test passing
- duplicate ability stacking regression test passing
- pool bonus tests passing
- content contract tests passing for shared, race, adventure, and profession modules
- at least 3 representative black-box character builds passing

Once that baseline exists, future refactors become much safer.

---

## 14. Final Recommendation

Build the test suite around the architecture you now have, not the one you started with.

The highest-leverage principle is:

- **unit tests protect contracts**
- **regression tests protect real bugs**
- **black-box tests protect user-visible behavior**
- **smoke tests protect your ability to keep moving quickly**

For this engine, the most important protected seams are:

- registry bootstrap and reload
- shared ability registration/grants
- deterministic rebuild order
- duplicate stacking
- derived/pool calculation correctness
- runtime/rebuild separation