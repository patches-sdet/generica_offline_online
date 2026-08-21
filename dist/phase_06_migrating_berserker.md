# Phase 6 - Migrating Berserker

## Goal
Use Berserker as the first end-to-end migration pilot from YAML content to typed Python definitions.

## Why Berserker is a good pilot
[`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) contains a representative mix of:
- active abilities
- passive abilities
- skill abilities
- grants
- scaling
- event-driven and attack-modifying effects

That makes it a strong proof point without forcing full-repository migration.

## Migration strategy

### Step 1: inventory the YAML
Break the file into four buckets:
- owner metadata
- ability metadata
- activation metadata
- effect definitions
- grants

### Step 2: rewrite one ability at a time
Do **not** try to translate the entire file in your head at once.

### Step 3: keep the migration mechanically traceable
For each migrated ability, be able to answer:
- which YAML fields became typed metadata?
- which YAML fields became effect specs?
- how does the compiler recreate the runtime behavior?

## Example conversion pattern: Furious Strike

### Source concept
[`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) describes a next-attack damage bonus based on progression level plus ability level.

### Example migrated sketch
**Example sketch — illustrative only**

```python
BERSERKER = JobDefinition(
    owner_type="adventure",
    owner_name="Berserker",
    abilities=(
        AbilityDefinition(
            name="Furious Strike",
            kind="active",
            required_level=1,
            description=(
                "Your next attack inflicts additional damage equal to your "
                "Berserker level plus the level of this skill."
            ),
            activation=ActivationSpec(
                cost=10,
                cost_pool="hp",
                duration="1 Attack",
                target="enemy",
            ),
            scales_with_level=True,
            effects=(
                ModifyNextAttackSpec(
                    damage_bonus=(
                        ProgressionLevelBonus("adventure", "Berserker", 1),
                        AbilityLevelBonus("Furious Strike", 1),
                    )
                ),
            ),
        ),
    ),
)
```

## Example conversion pattern: grants
The `grants` block in [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) should become explicit grant objects rather than ad hoc dicts.

**Example sketch**

```python
grants=(
    GrantSpec(name="Growl", required_level=1),
    GrantSpec(name="Rage", required_level=1),
    GrantSpec(name="Toughness", required_level=5),
    GrantSpec(name="Fast as Death", required_level=15),
)
```

## Example conversion pattern: passive event ability
`Power From Pain` shows an event-driven pattern. For the pilot, keep the typed shell strong even if the event condition or payload needs a transitional helper.

**Example sketch**

```python
AbilityDefinition(
    name="Power From Pain",
    kind="passive",
    required_level=1,
    description="Whenever the Berserker loses 10 or more hit points...",
    effects=(
        OnEventSpec(
            event_name="hp_lost",
            effect=ApplyStateSpec(state="power_from_pain_active"),
        ),
    ),
)
```

## Beginner warning
If a Berserker ability feels hard to migrate, that is useful information. It may mean:
- the effect-spec model needs one more concept
- the compiler needs one more translation rule
- the original YAML shape was hiding complexity

That is exactly why a pilot migration is valuable.

## Exit criteria for this phase
- Berserker exists as typed Python content.
- Its grants are explicit.
- Its hardest effects are represented honestly, even if some internals remain transitional.
