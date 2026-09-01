# Phase 7 - Updating Bootstrap and Registry Flow

## Goal
Load migrated typed definitions through the existing registry/bootstrap path without breaking the rest of the repository.

## Why this phase matters
The migration only becomes real when the new content can participate in normal initialization.

The current bootstrap path is centered on [`initialize_content_registries()`](src/domain/content_registry.py:229), which imports shared and progression packages and relies on registration side effects.

## Recommended approach
Keep bootstrap changes narrow.

The safest path is:
1. add a migrated Python content module
2. import it through the existing package/registry flow
3. compile its typed definitions into current runtime objects during module import or explicit registration

## What not to do
- do not redesign all of [`src/domain/content_registry.py`](src/domain/content_registry.py)
- do not mix migration work with unrelated registry cleanup
- do not require all content families to migrate at once

## Bridge-to-registry idea
The compiler can return compiled abilities and grants, and a small registration helper can apply them using current registration patterns already used around [`build_job()`](src/domain/abilities/builders/_job_builder.py:104).

## Example registration sketch
**Example sketch**

```python
def register_job_definition(job_def):
    abilities, grants = compile_job(job_def)

    for ability in abilities:
        register_ability(ability)

    for grant in grants:
        register_progression_ability_grant(
            job_def.owner_type,
            job_def.owner_name,
            grant.name,
            required_level=grant.required_level,
        )
```

## Repository-specific caution
The current repository still contains mixed ability-loading approaches:
- Python package imports in [`initialize_content_registries()`](src/domain/content_registry.py:229)
- YAML loading in [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9)
- dict-based builder behavior in [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39)

The point of this phase is not to remove all old paths immediately. The point is to prove the new path can coexist safely.

## Exit criteria for this phase
- Berserker can be registered through the normal bootstrap path.
- The rest of the repository still loads.
- The new path is clear enough to repeat for the next job.
