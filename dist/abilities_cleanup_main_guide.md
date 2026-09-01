# Abilities System Cleanup Main Guide

## Purpose
This guide consolidates the architectural recommendation and beginner cleanup guide for the abilities system.

The chosen direction is **Option C**:

- keep the current Python engine
- add a typed, code-first definition layer in Python
- compile that layer into the existing runtime [`Ability`](src/domain/abilities/factory.py:6) objects
- migrate content incrementally, starting with Berserker
- do **not** make YAML the long-term source of truth
- do **not** attempt a full rewrite

This is the right fit for this repository because the system already has useful Python seams in [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39), [`make_ability()`](src/domain/abilities/factory.py:52), and [`initialize_content_registries()`](src/domain/content_registry.py:229), while the current YAML path in [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9) is too weakly typed to be a good foundation for a learning-oriented cleanup.

---

## 1. The recommendation in one sentence
Build a thin typed-definition layer in Python, add structured effect specs plus a compiler/bridge, migrate one job at a time, and use Berserker from [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) as the first pilot.

---

## 2. Why Option C is the best choice here

## What the repository already tells us
- The current runtime ability surface is already Python-native through [`Ability`](src/domain/abilities/factory.py:6).
- The current builder in [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39) expects Python callables and dynamic objects, not a rich static schema.
- The YAML path in [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9) is minimal and only loads files ending in `*.yaml`, while at least one key file is actually [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml), which shows the content system is already in a transitional state.
- Registry bootstrap currently imports Python packages directly in [`initialize_content_registries()`](src/domain/content_registry.py:229), which makes Python-first migration much easier than a whole new content platform.

## Why not YAML-first migration
YAML-first would force the cleanup to answer too many hard questions at once:
- strict schema design
- expression language design for dynamic behavior
- validation tooling
- serialization rules for Python lambdas and event hooks
- migration of mixed legacy content

That would create a “tooling project” before fixing the actual maintainability problem.

## Why not full rewrite
A full rewrite would be a poor fit for a solo developer with a 2-month stakeholder window because it multiplies risk across:
- engine behavior
- content compatibility
- bootstrap behavior
- tests
- delivery confidence

The current project already has meaningful test anchors such as [`tests/regression/test_deterministic_rebuild.py`](tests/regression/test_deterministic_rebuild.py), [`tests/smoke/test_bootstrap.py`](tests/smoke/test_bootstrap.py), and [`tests/unit/content/test_registry_bootstrap.py`](tests/unit/content/test_registry_bootstrap.py). Option C preserves those anchors.

---

## 3. What success looks like after 2 months

By the end of the first 2 months, a strong result is:

1. one typed-definition module exists and is understandable
2. one structured effect-spec layer exists and is understandable
3. one compiler/bridge can produce existing-style [`Ability`](src/domain/abilities/factory.py:6) objects
4. Berserker is migrated as a reference implementation
5. bootstrap can load the migrated Berserker content without breaking the rest of the repository
6. tests prove parity for unlocks, grants, metadata, and core effect behavior
7. stakeholder-facing docs clearly explain that the system is becoming safer without a rewrite

That is enough to show momentum, reduce future risk, and give the stakeholder a believable next-step plan.

---

## 4. Product scope for this cleanup

## In scope
- documenting the direction clearly
- creating typed Python definition objects
- creating typed effect specs
- creating a compiler/bridge to current runtime objects
- migrating Berserker first
- keeping registry bootstrap compatible
- adding focused tests for migration safety
- preparing a stakeholder presentation path

## Out of scope
- full migration of all abilities within 2 months
- replacing the full runtime execution system in [`execute_ability()`](src/application/runtime.py:186)
- replacing deterministic rebuild in [`recalculate()`](src/domain/calculations/__init__.py:18)
- designing a general-purpose scripting language for abilities
- trying to solve every legacy inconsistency immediately

This boundary is aligned with the repository’s broader “incremental rather than sweeping” direction in [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md) and [`dist/compiled_update.md`](dist/compiled_update.md).

---

## 5. Target architecture

The intended flow is:

1. author ability content as typed Python definition objects
2. author ability effects as typed effect-spec objects
3. compile definitions into current runtime [`Ability`](src/domain/abilities/factory.py:6) objects
4. register those compiled abilities through the existing content registry flow
5. migrate content family by content family

## Conceptual layers

### Layer A: raw authoring layer
New typed objects such as `AbilityDefinition`, `ActivationSpec`, `GrantSpec`, and effect spec classes.

### Layer B: compiler/bridge layer
Functions that translate typed definitions into current runtime shapes expected by [`make_ability()`](src/domain/abilities/factory.py:52) and registry registration helpers used near [`build_job()`](src/domain/abilities/builders/_job_builder.py:104).

### Layer C: existing engine/runtime layer
Current ability objects, existing registry behavior, and current tests.

That means the cleanup adds a safer authoring surface **above** the current engine instead of replacing the engine immediately.

---

## 6. Beginner-friendly sketches of the new model

## Example: typed definition objects
**Example sketch — not copied from live code yet**

```python
from dataclasses import dataclass, field
from typing import Literal


AbilityKind = Literal["active", "passive", "skill"]


@dataclass(frozen=True, slots=True)
class ActivationSpec:
    cost: int = 0
    cost_pool: str | None = None
    duration: str | None = None
    target: str = "self"


@dataclass(frozen=True, slots=True)
class AbilityDefinition:
    name: str
    kind: AbilityKind
    required_level: int
    description: str
    activation: ActivationSpec = ActivationSpec()
    scales_with_level: bool = False
    effects: tuple[object, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class JobDefinition:
    owner_type: str
    owner_name: str
    abilities: tuple[AbilityDefinition, ...]
    grants: tuple[object, ...] = field(default_factory=tuple)
```

Why this helps:
- your editor can autocomplete fields
- mistakes become visible earlier
- content shape is readable without interpreting arbitrary dictionaries
- tests can compare real objects instead of loosely structured nested mappings

## Example: effect specs
**Example sketch — not final API**

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FlatBonus:
    amount: int


@dataclass(frozen=True, slots=True)
class ProgressionLevelBonus:
    source_type: str
    source_name: str
    multiplier: int = 1


@dataclass(frozen=True, slots=True)
class AbilityLevelBonus:
    ability_name: str
    multiplier: int = 1


@dataclass(frozen=True, slots=True)
class ModifyNextAttackSpec:
    damage_bonus: tuple[object, ...]
```

The main idea is that dynamic pieces become named spec types instead of unvalidated nested dict fragments.

## Example: compiler/bridge
**Example sketch — thin wrapper around current runtime model**

```python
def compile_ability(defn: AbilityDefinition, owner_name: str, source_type: str):
    execute = None
    effect_generator = None

    if defn.kind == "passive":
        effect_generator = compile_passive_effects(defn.effects, owner_name, defn.name)
    else:
        execute = compile_active_effects(defn.effects, owner_name, defn.name)

    return make_ability(
        name=defn.name,
        unlock_condition=make_default_unlock(source_type, owner_name, defn.required_level),
        execute=execute,
        effect_generator=effect_generator,
        cost=defn.activation.cost,
        cost_pool=defn.activation.cost_pool,
        duration=defn.activation.duration,
        description=defn.description,
        is_passive=(defn.kind == "passive"),
        is_skill=(defn.kind == "skill"),
        target_type=defn.activation.target,
        scales_with_level=defn.scales_with_level,
    )
```

This keeps the new layer small and practical.

---

## 7. Recommended file-level implementation approach

These are suggested destination areas, chosen to fit the existing repository shape.

## Keep and reuse
- [`src/domain/abilities/factory.py`](src/domain/abilities/factory.py)
- [`src/domain/abilities/builders/_job_builder.py`](src/domain/abilities/builders/_job_builder.py)
- [`src/domain/content_registry.py`](src/domain/content_registry.py)

## Reduce long-term reliance on
- [`src/domain/abilities/loader.py`](src/domain/abilities/loader.py)
- YAML content such as [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml)

## Good candidate areas for new code later
- `src/domain/abilities/definitions/` for typed definition classes
- `src/domain/abilities/effect_specs/` for structured effect spec classes
- `src/domain/abilities/compiler.py` for the bridge layer
- `src/domain/abilities/adventure/berserker.py` for the migrated Berserker definition

Those are recommendations for future source work only. This document set does not change source code.

---

## 8. Sequential implementation plan

Follow the phases in this exact order:

1. architectural direction
2. scope and deferments
3. typed definitions layer
4. effect specs layer
5. compiler/bridge
6. Berserker migration
7. bootstrap/registry updates
8. tests and validation
9. stakeholder presentation roadmap

The linked explainers are:
- [`dist/phase_01_architectural_direction.md`](dist/phase_01_architectural_direction.md)
- [`dist/phase_02_product_scoping_and_deferments.md`](dist/phase_02_product_scoping_and_deferments.md)
- [`dist/phase_03_typed_definitions_layer.md`](dist/phase_03_typed_definitions_layer.md)
- [`dist/phase_04_effect_specs.md`](dist/phase_04_effect_specs.md)
- [`dist/phase_05_compiler_bridge.md`](dist/phase_05_compiler_bridge.md)
- [`dist/phase_06_migrating_berserker.md`](dist/phase_06_migrating_berserker.md)
- [`dist/phase_07_bootstrap_and_registry_updates.md`](dist/phase_07_bootstrap_and_registry_updates.md)
- [`dist/phase_08_testing_and_validation.md`](dist/phase_08_testing_and_validation.md)
- [`dist/phase_09_stakeholder_presentation_roadmap.md`](dist/phase_09_stakeholder_presentation_roadmap.md)

---

## 9. Berserker is the right migration pilot

[`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) is a strong first pilot because it includes:
- active abilities
- passive abilities
- skill-like abilities
- grants
- scaling examples
- effect variety

That makes it broad enough to prove the architecture, but still narrow enough for a solo developer to finish.

The goal is not “migrate the hardest thing imaginable.”
The goal is “migrate one representative job thoroughly enough that the next job becomes easier.”

---

## 10. How to present this to a stakeholder

When speaking to a non-technical stakeholder, describe the plan like this:

1. the existing engine works, but content authoring is fragile
2. a full rewrite would create unnecessary risk
3. the team is introducing typed content definitions to reduce mistakes and speed up future changes
4. the migration is incremental, so the product keeps moving
5. Berserker is the pilot that proves the path
6. after the pilot, the same pattern can be repeated safely for other jobs

This frames the work as risk reduction plus future delivery acceleration.

---

## 11. Practical 2-month roadmap

### Weeks 1-2
- finalize structure and naming for typed definitions
- write the first small definition objects
- write the first effect spec objects

### Weeks 3-4
- build the compiler/bridge
- prove it can emit current-style [`Ability`](src/domain/abilities/factory.py:6) objects
- verify the bridge can cover at least one active and one passive case

### Weeks 5-6
- migrate Berserker
- keep compatibility with current registry/bootstrap flow
- fill test gaps discovered by the migration

### Weeks 7-8
- harden tests
- document outcomes
- prepare stakeholder summary: problem, approach, proof, next steps

---

## 12. Decision checklist

Before starting source changes, the solo developer should be able to say “yes” to these:

- I understand why Option C is chosen.
- I know what is deliberately deferred.
- I can explain the three layers: definitions, effect specs, compiler.
- I know Berserker is the first migration target.
- I know tests must prove parity before wider migration.
- I can explain the plan to a stakeholder in plain English.

If those are all true, the plan is ready to execute.
