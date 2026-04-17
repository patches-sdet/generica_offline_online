Yes — if this is the rule for **all leveled skills**, then it should absolutely be generalized.

What you have is not really a “Growl exception.” It is a broader progression model for **leveled abilities/skills**:

```text
first grant establishes the primary source
additional grants add +5 each
use in play adds independent use ranks
effective level is derived from those inputs
```

So the design note should shift from:

```text
source-aware shared ability progression
```

to something more general like:

```text
leveled ability progression model
```

or:

```text
source-aware leveled skill progression
```

That will make it much cleaner and prevent you from having to rewrite the note later when the same rule applies to more than Growl.

Below is a **paste-ready generalized replacement**.

---

# Leveled Ability Progression Model — Design Note

This note defines a generic progression model for **leveled abilities / skills**.

It applies to abilities that:

* are granted by one or more progression sources
* gain `+5` effective levels from duplicate grants
* also gain levels through use during play

This is intended as the standard model for **all leveled skills**, not a special-case rule for a single ability.

---

## Core Rule

For a leveled ability, the effective level is derived from three inputs:

```text
effective ability level
= primary source contribution
+ duplicate grant bonus
+ use ranks
```

Where:

* the **primary source** is the first progression that granted the ability
* each additional source that grants the same ability adds `+5`
* use during play adds independent **use ranks**

---

## Why This Model Exists

A flat field like:

```python
character.ability_levels["Ability Name"]
```

is useful as a derived output, but it is not rich enough to serve as the only source of truth for leveled skills.

A single number does not preserve:

* which source granted the ability first
* how many duplicate grants have occurred
* how much of the ability’s level came from use progression

For leveled skills, those distinctions matter.

So the engine should store the persistent progression inputs separately and derive the final effective level during rebuild.

---

## Deterministic Rule

The engine rule is:

```text
first grant wins
```

Meaning:

* the first progression that grants the ability becomes the permanent primary source
* later grants do not replace that source
* later grants only add duplicate bonus

This keeps source attribution stable and avoids rebuild drift.

---

## Effective Level Formula

For any leveled ability:

```text
effective level
= base from primary source
+ 5 * duplicate source count
+ use ranks
```

Example:

```text
primary source level: 1
duplicate sources: 2
use ranks: 3
```

Result:

```text
1 + 10 + 3 = 14
```

---

## Scope

This model applies to:

```text
leveled skills
leveled shared abilities
leveled progression-granted abilities
```

It does **not** need to apply to:

```text
non-leveled abilities
one-off actives with fixed strength
passives that do not scale by level
```

Non-leveled abilities still deduplicate as a single instance, but do not accumulate use ranks or effective levels in this way.

---

## Proposed Character Field Layout

Store the persistent inputs separately.

### 1. Ability provenance

Tracks the primary source and duplicate sources for each leveled ability.

```python
ability_provenance: dict[str, dict] = field(default_factory=dict)
```

Recommended payload:

```python
{
    "Growl": {
        "primary_source": ("race", "Bear"),
        "duplicate_sources": {
            ("adventure", "Berserker"),
        },
    },
    "Quickdraw": {
        "primary_source": ("adventure", "Archer"),
        "duplicate_sources": {
            ("adventure", "Assassin"),
        },
    },
}
```

Notes:

* `primary_source` is the first grant source
* `duplicate_sources` contains all later unique sources
* the primary source must not also appear in `duplicate_sources`

---

### 2. Ability use ranks

Tracks progression earned through use in play.

```python
ability_use_ranks: dict[str, int] = field(default_factory=dict)
```

Example:

```python
{
    "Growl": 3,
    "Rage": 1,
}
```

Notes:

* this stores only use-earned ranks
* it does not store duplicate-grant bonuses
* it does not store base source contribution

---

## Proposed Character Dataclass Snippet

```python
from dataclasses import dataclass, field

@dataclass(slots=True)
class Character:
    # ... existing fields ...

    ability_provenance: dict[str, dict] = field(default_factory=dict)
    ability_use_ranks: dict[str, int] = field(default_factory=dict)
```

---

## Provenance Payload Contract

Use this structure consistently:

```python
{
    "primary_source": (ptype, progression_name),
    "duplicate_sources": set[tuple[str, str]],
}
```

Where `ptype` is one of:

```text
race
adventure
profession
advanced
```

Example:

```python
character.ability_provenance["Growl"] = {
    "primary_source": ("race", "Bear"),
    "duplicate_sources": {("adventure", "Berserker")},
}
```

---

## Derived Effective Level Helper

Add a helper that computes the level of any leveled ability from its persistent inputs.

```python
def get_leveled_ability_effective_level(character, ability_name: str) -> int:
    provenance = character.ability_provenance.get(ability_name)
    if not provenance:
        return 0

    primary_source = provenance.get("primary_source")
    if not primary_source:
        return 0

    duplicate_sources = provenance.get("duplicate_sources", set())
    use_ranks = int(character.ability_use_ranks.get(ability_name, 0))

    ptype, progression_name = primary_source
    base = max(1, int(character.get_progression_level(ptype, progression_name, 0)))

    duplicate_bonus = len(duplicate_sources) * 5

    return base + duplicate_bonus + use_ranks
```

---

## Why This Helper Is Correct

It derives the final effective level from the three true inputs:

* current primary source contribution
* current duplicate grant count
* current use-earned ranks

This keeps leveled abilities:

```text
deterministic
rebuild-safe
explainable
extensible
```

It also lets source contribution remain dynamic.

Example:

If the primary source is:

```python
("adventure", "Berserker")
```

and Berserker later rises from level 1 to level 4, then the ability’s base contribution rises automatically during rebuild.

---

## Grant Recording Helper

When a progression grants a leveled ability, record provenance like this:

```python
def record_leveled_ability_grant(
    character,
    ability_name: str,
    source_type: str,
    progression_name: str,
) -> None:
    source_key = (source_type, progression_name)

    entry = character.ability_provenance.setdefault(
        ability_name,
        {
            "primary_source": None,
            "duplicate_sources": set(),
        },
    )

    if entry["primary_source"] is None:
        entry["primary_source"] = source_key
        return

    if entry["primary_source"] != source_key:
        entry["duplicate_sources"].add(source_key)
```

This preserves the rule:

```text
first grant wins
```

while ensuring later sources count toward duplicate bonus.

---

## Use Progression Helper

Use-earned levels should be tracked separately.

```python
def add_ability_use_ranks(character, ability_name: str, ranks: int = 1) -> None:
    if ranks <= 0:
        raise ValueError(f"Use ranks must be positive for {ability_name!r}: {ranks}")

    current = int(character.ability_use_ranks.get(ability_name, 0))
    character.ability_use_ranks[ability_name] = current + ranks
```

This avoids mixing use progression with grant progression.

---

## Rebuild Integration

During rebuild:

1. progression grants are resolved
2. provenance for leveled abilities is recorded
3. duplicate grant counts are determined
4. use ranks are read
5. final `ability_levels[...]` values are derived from the helper

For leveled abilities, this means:

```text
ability_levels is derived output
not sole source of truth
```

That keeps the rest of the engine compatible with existing `ability_levels[...]` consumers while improving the underlying model.

---

## Practical Scaling Rule for Abilities

For any leveled ability that scales with its level, use:

```python
scale_fn=lambda c: get_leveled_ability_effective_level(c, "Ability Name")
```

instead of relying on a manually flattened level source.

Example:

```python
scale_fn=lambda c: get_leveled_ability_effective_level(c, "Growl")
```

---

## Non-Leveled Ability Rule

Non-leveled abilities do not use this model.

They still follow shared deduplication rules structurally, but they do not accumulate:

* use ranks
* effective level scaling
* source-aware leveled progression

So this model should be applied only to abilities that are explicitly marked as leveled.

---

## Summary

Use this as the generic model for all leveled skills:

```text
effective level
= primary source contribution
+ 5 per extra grant source
+ use ranks
```

Store:

* ability provenance
* ability use ranks

Derive during rebuild:

* final effective `ability_levels[...]`

This gives the engine a progression model that is:

```text
generic
deterministic
source-aware
compatible with rebuild
ready for all leveled skills
```