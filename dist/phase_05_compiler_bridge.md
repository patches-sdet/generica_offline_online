# Phase 5 - Creating the Compiler / Bridge

## Goal
Translate typed definition objects and effect specs into the current runtime [`Ability`](src/domain/abilities/factory.py:6) objects so the rest of the repository can keep working.

## Why this phase is the heart of Option C
Without the compiler/bridge, typed definitions are just nice data objects. The bridge is what lets the project gain safer authoring **without** rewriting the engine.

## What the bridge should consume
- typed `JobDefinition`
- typed `AbilityDefinition`
- typed effect specs

## What the bridge should emit
- runtime [`Ability`](src/domain/abilities/factory.py:6) objects
- progression grants registered similarly to the behavior in [`build_job()`](src/domain/abilities/builders/_job_builder.py:104)

## Key repository seam to reuse
The current runtime creation seam is [`make_ability()`](src/domain/abilities/factory.py:52). Reusing it keeps the migration safer and preserves compatibility with current tests and consumers.

## Example compiler shape
**Example sketch — not final implementation**

```python
def compile_job(job_def):
    compiled_abilities = []

    for ability_def in job_def.abilities:
        compiled_abilities.append(
            compile_ability(
                ability_def,
                owner_name=job_def.owner_name,
                source_type=job_def.owner_type,
            )
        )

    return compiled_abilities, job_def.grants


def compile_ability(defn, owner_name: str, source_type: str):
    unlock_condition = make_default_unlock(source_type, owner_name, defn.required_level)

    if defn.kind == "passive":
        effect_generator = compile_passive_effects(defn.effects, owner_name, defn.name)
        execute = None
    else:
        effect_generator = None
        execute = compile_active_effects(defn.effects, owner_name, defn.name)

    return make_ability(
        name=defn.name,
        unlock_condition=unlock_condition,
        execute=execute,
        effect_generator=effect_generator,
        cost=defn.activation.cost,
        cost_pool=defn.activation.cost_pool,
        duration=defn.activation.duration,
        description=defn.description,
        target_type=defn.activation.target,
        scales_with_level=defn.scales_with_level,
        is_passive=(defn.kind == "passive"),
        is_skill=(defn.kind == "skill"),
    )
```

## Important design constraint
The bridge should be thin.

If it becomes full of gameplay decisions, the migration will create a second engine instead of a cleaner authoring layer.

## What to keep out of the bridge
- broad registry redesign
- custom global state management
- new progression rules
- speculative runtime refactors unrelated to the pilot

## Passive vs active handling
The current runtime shape distinguishes `execute` and `effect_generator` in [`Ability`](src/domain/abilities/factory.py:6) and validates that split in [`validate_ability_definition()`](src/domain/abilities/factory.py:30). The bridge should preserve that split clearly.

## Beginner note
Think of the bridge as an adapter. Its job is not to be clever. Its job is to take safer inputs and produce familiar outputs.

## Exit criteria for this phase
- You can compile one passive and one active definition.
- The output shape matches what [`make_ability()`](src/domain/abilities/factory.py:52) expects.
- You are ready to test a real content migration with Berserker.
