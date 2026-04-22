# Next 5 Implementation Steps — Leveled Ability Progression Refactor

## Goal

Before continuing the broad job/shared-ability normalization pass, stabilize the engine’s **leveled ability scaling substrate** so that abilities marked:

```python
scales_with_level = True
```

can scale correctly from:

```text
primary source contribution
+ 5 per duplicate grant source
+ use-earned ranks
```

This should be treated as the current highest-priority architectural task, because the newer shared/job authoring rules still depend on a stable read interface while the new design note changes the internal truth for leveled ability scaling.

---

## Step 1 — Define the new Character-side storage model

Add explicit storage for leveled-ability provenance and future use progression.

### Add fields

Planned shape:

```python
character.ability_provenance: dict[str, dict]
character.ability_use_ranks: dict[str, int]
```

Recommended initial structure:

```python
character.ability_provenance["Growl"] = {
    "primary_source": ("race", "Bear"),
    "duplicate_sources": {("adventure", "Berserker")},
}
```

And:

```python
character.ability_use_ranks["Growl"] = 0
```

### Why this comes first

Right now the engine can tell:

* which progressions a character has
* which progressions grant an ability
* in some cases the highest granting progression by type

But it **cannot** truthfully answer:

```text
which source granted this ability first?
```

That missing fact is the key blocker for shared leveled abilities like Growl / Friendly Smile / future cross-progression shared skills. The design note explicitly identifies primary source tracking as part of the intended long-term model. 

---

## Step 2 — Add a minimal provenance-aware helper API

Do not jump straight to broad refactors. First add the engine helpers that define the new truth.

### Recommended helpers

Add a small, explicit helper surface, for example:

```python
get_primary_progression_for_ability(character, ability_name)
get_primary_progression_level_for_ability(character, ability_name, default=0)
get_duplicate_grant_count(character, ability_name)
get_ability_use_ranks(character, ability_name, default=0)
get_leveled_ability_effective_level(character, ability_name, default=0)
```

### Effective-level target formula

```text
effective level
=
primary source contribution
+ 5 * duplicate grant count
+ use ranks
```

This is the core formula described in the leveled-ability design summary. 

### Important constraint

Do **not** delete or break the existing public consumer interface yet.

The style guides still expect downstream ability definitions and helpers to be able to read effective ability level through the normal public path. The docs explicitly say `ability_levels[...]` should remain the canonical downstream read interface even after internal semantics change.

---

## Step 3 — Rebuild `ability_levels[...]` as derived output

Once the provenance helpers exist, change rebuild so that leveled ability output is recomputed rather than treated as the primitive source of truth.

### New rule

For abilities with:

```python
scales_with_level = True
```

the value in:

```python
character.ability_levels[ability_name]
```

should become **derived output**, not primary storage. This is the explicit design target in the leveled-ability note. 

### Practical implementation target

Inside the rebuild/ability reconstruction pass:

* determine which abilities are present
* determine provenance for leveled abilities
* compute duplicate grant count
* pull use ranks
* write derived effective level into `character.ability_levels[...]`

### Why this matters

This step preserves compatibility with current authoring patterns while switching the internal source of truth to the new provenance model. That matches the shared authoring guide’s “consumer interface remains stable; internal scaling semantics change” direction. 

---

## Step 4 — Update shared ability scaling rules before more content refactors

Once the substrate exists, update shared abilities that are semantically sensitive to source-aware scaling.

### Prioritize these categories

1. **Shared leveled abilities already duplicated across progressions**

   * Growl
   * Fast as Death
   * Rage
   * other `scales_with_level=True` shared abilities

2. **Shared abilities that should scale from primary grant progression rather than total effective level**

   * Friendly Smile-style cases
   * any future “first granting source determines bonus” design

3. **Shared abilities incorrectly hardcoding a progression**

   * anything currently binding directly to a specific job when the grant source may vary later

### Rule to apply

For shared abilities:

* use `get_leveled_ability_effective_level(...)` when the ability should scale from total effective ability level
* use `get_primary_progression_level_for_ability(...)` when the ability should scale from the first granting source
* do **not** hardcode a specific progression unless the ability is conceptually job-coupled by design

This follows directly from the updated shared-ability guide, which now distinguishes the public scaling interface from the internal source-aware model. 

---

## Step 5 — Resume the content normalization pass only after the substrate is stable

Once steps 1–4 are done, continue the remaining job/shared cleanup work.

### Why this is last

Most of the refactors already done were still useful structurally:

* cleaner DSL usage
* fewer bespoke effect classes
* more consistent `apply_state(...)`/`skill_check(...)`/`modify_next_attack(...)` usage
* better separation between metadata and direct effects

But those refactors should now be treated as **provisional authoring cleanup**, not final scaling truth, until the provenance model is actually live. The job and shared authoring docs remain useful, but they need to sit on top of the corrected leveled-ability substrate.

### Resume order recommendation

After the substrate lands:

1. shared leveled abilities
2. remaining adventure jobs
3. profession jobs that rely on shared leveled skills
4. race-granted leveled abilities
5. advanced jobs

This keeps the most scaling-sensitive content aligned first.

---

# Practical Development Recommendation

Treat the current repo state as:

```text
authoring layer mostly improved
scaling substrate still incomplete
```

So the next implementation milestone should be:

```text
“leveled ability provenance + derived effective level”
```

not:

```text
“finish refactoring every remaining job first”
```

That is the cleanest way to avoid doing a second broad cleanup pass later. The documents you shared strongly support this sequencing: authoring syntax can remain stable, but internal semantics for `scales_with_level=True` need to be corrected before the content pass is considered complete.

---

# One-sentence summary

Stop broad content cleanup temporarily, implement provenance-aware leveled ability scaling first, rebuild `ability_levels[...]` as derived output, then return to shared/job normalization on top of that foundation.
