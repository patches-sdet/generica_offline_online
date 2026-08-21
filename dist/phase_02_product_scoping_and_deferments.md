# Phase 2 - Product Scoping and Deferments

## Goal
Prevent the cleanup effort from becoming an open-ended architecture rewrite.

## In scope for the first 2 months
- define the new typed authoring model
- define structured effect specs
- compile them into the current runtime surface
- migrate Berserker as the proof point
- prove it through tests
- prepare a stakeholder-ready explanation

## Explicitly deferred

### Deferred platform work
- replacing the whole runtime execution flow in [`execute_ability()`](src/application/runtime.py:186)
- redesigning the deterministic rebuild pipeline around [`recalculate()`](src/domain/calculations/__init__.py:18)
- migrating every job, race, profession, and advanced class immediately
- building a general visual content editor
- designing a powerful embedded DSL for ability scripting

### Deferred content work
- broad cleanup of every legacy YAML file
- normalization of every shared ability definition
- total removal of old builder paths in one shot

## Why deferments matter
A solo developer can finish an incremental pilot. A solo developer usually cannot finish “clean up all ability architecture everywhere” in 2 months while still giving the stakeholder confidence.

## Recommended milestone boundary

### Milestone A
Typed definitions and effect specs exist.

### Milestone B
Compiler/bridge produces current-style runtime objects.

### Milestone C
Berserker is migrated and passing tests.

### Milestone D
Stakeholder can see one working example plus a repeatable migration pattern.

## Anti-scope-creep checklist
If a task does not directly help one of the four milestones above, defer it unless it blocks the pilot.

## Repository-specific warning signs
Be careful not to accidentally turn this effort into:
- a replacement for [`src/domain/content_registry.py`](src/domain/content_registry.py)
- a rewrite of [`src/application/runtime.py`](src/application/runtime.py)
- a cleanup of every file under [`src/domain/abilities/`](src/domain/abilities)

## Exit criteria for this phase
- You have a written “not now” list.
- You can reject tempting side work without guilt.
- You can explain that the pilot proves the pattern before wider migration.
