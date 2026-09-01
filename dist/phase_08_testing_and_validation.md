# Phase 8 - Testing and Validation

## Goal
Prove that the migration reduces risk instead of creating hidden behavior changes.

## Why this phase matters
The repository already has meaningful tests around bootstrap, registry behavior, and deterministic rebuild, including [`tests/smoke/test_bootstrap.py`](tests/smoke/test_bootstrap.py), [`tests/regression/test_registry_reload.py`](tests/regression/test_registry_reload.py), and [`tests/unit/content/test_registry_bootstrap.py`](tests/unit/content/test_registry_bootstrap.py).

This cleanup should add to that confidence, not bypass it.

## What to test first

### 1. Definition-level tests
Test that typed definition objects hold the expected shape.

### 2. Compiler tests
Test that compiling a definition produces the right runtime [`Ability`](src/domain/abilities/factory.py:6) metadata.

### 3. Registration tests
Test that grants and compiled abilities register correctly.

### 4. Pilot parity tests
Test that migrated Berserker behavior matches the old content expectations for key cases.

## Example unit test sketches
**Example sketches — not live tests**

```python
def test_compile_active_definition_sets_runtime_metadata():
    ability = compile_ability(FURIOUS_STRIKE, owner_name="Berserker", source_type="adventure")

    assert ability.name == "Furious Strike"
    assert ability.cost == 10
    assert ability.cost_pool == "hp"
    assert ability.target_type == "enemy"
    assert ability.is_passive is False
```

```python
def test_compile_passive_definition_uses_effect_generator():
    ability = compile_ability(POWER_FROM_PAIN, owner_name="Berserker", source_type="adventure")

    assert ability.execute is None
    assert ability.effect_generator is not None
    assert ability.is_passive is True
```

```python
def test_berserker_grants_register_at_expected_levels(initialized_content):
    grants = get_progression_grants_for("adventure", "Berserker")

    assert ("Growl", 1) in grants
    assert ("Toughness", 5) in grants
```

## Suggested real test categories for this repository
- add focused unit tests near [`tests/unit/content/`](tests/unit/content)
- add bridge or compiler tests in a small new content-focused test module
- extend bootstrap safety tests near [`tests/smoke/test_bootstrap.py`](tests/smoke/test_bootstrap.py)
- add regression tests if migration order or registration idempotency becomes fragile

## What not to over-test at first
- every runtime edge case in [`execute_ability()`](src/application/runtime.py:186)
- every progression family in the repository
- every historical YAML file

Test the pilot deeply enough to build confidence, then expand.

## Validation checklist
- Compiled metadata matches expectations.
- Passive/active split is preserved.
- Grants register at the correct levels.
- Bootstrap still succeeds.
- Existing regression tests still pass.

## Exit criteria for this phase
- Berserker migration has focused tests.
- Bootstrap compatibility is verified.
- You have evidence strong enough to show the stakeholder that this is safer, not just cleaner.
