# Phase 1 - Architectural Direction

## Goal
Lock the team onto **Option C**: Python-first cleanup with code-first typed definition objects.

## Core decision
Build a safer authoring layer in Python and compile it into the current runtime [`Ability`](src/domain/abilities/factory.py:6) model.

## Why this direction fits this repository

### Existing code already favors Python composition
- [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39) builds runtime objects from Python dictionaries and callables.
- [`make_ability()`](src/domain/abilities/factory.py:52) already provides a stable runtime creation seam.
- [`initialize_content_registries()`](src/domain/content_registry.py:229) already bootstraps content through Python package imports.

### Existing YAML is not strong enough to be the strategic source of truth
- [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9) is very thin.
- YAML content such as [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) contains behavior-heavy structures that are hard to validate and evolve cleanly.

## Decision summary table

| Option | Decision | Why |
|---|---|---|
| YAML-first migration | No | Too much schema/tooling risk for a solo developer |
| Full rewrite | No | Too much delivery and compatibility risk |
| Python-first typed definitions | Yes | Reuses current engine while making authoring safer |

## What this phase should produce
- one clear sentence explaining the chosen approach
- one picture in your head of the three target layers
- agreement that the first implementation target is a migration pilot, not a rewrite

## Three-layer mental model

### 1. Definition layer
Typed content objects, such as `JobDefinition` and `AbilityDefinition`.

### 2. Effect-spec layer
Typed effect descriptions, such as `ModifyNextAttackSpec`.

### 3. Compiler/bridge layer
Translation into current runtime [`Ability`](src/domain/abilities/factory.py:6) objects.

## Beginner explanation
If YAML is “raw text content” and the current engine is “the thing that already runs the game,” then Option C adds a safer middle step: Python objects that are easier to read, validate, and test.

## Example architectural sketch
**Example sketch**

```text
typed Python content -> compiler/bridge -> current Ability objects -> existing registry/bootstrap
```

## Exit criteria for this phase
- You can explain the plan in under 60 seconds.
- You know why the team is not doing YAML-first or rewrite-first.
- You can point to [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39) and [`make_ability()`](src/domain/abilities/factory.py:52) as the current bridge targets.
