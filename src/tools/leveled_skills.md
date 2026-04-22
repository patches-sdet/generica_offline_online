# Generica Offline Online — Leveled Ability Progression Model (Design Summary — No Code Changes Yet)

## Context

Shared abilities currently follow this stacking behavior:

```text
initial grant = level 1
each additional grant = +5 levels
```

Example:

```text
Bear grants Growl
Berserker grants Growl
→ Growl level = 6
```

This behavior is already validated by existing stacking tests.

However, the desired long-term model for **leveled abilities** expands this to support:

```text
primary source tracking
duplicate grant bonuses
use-based progression
```

This discussion established a **proposed generalized progression model**, but **no engine code has been modified yet**.

---

# Proposed Rule for Leveled Abilities (Design Target)

For any ability marked:

```python
scales_with_level = True
```

effective level should eventually be derived from:

```text
primary source contribution
+ 5 per additional grant source
+ use-earned ranks
```

This replaces the assumption that effective level is permanently stored as:

```python
character.ability_levels["Ability Name"]
```

Instead:

```text
ability_levels[...] should become derived output
```

This is a **planned architectural direction**, not current behavior.

---

# Primary Source Rule (Proposed)

The first progression that grants a leveled ability becomes its:

```text
primary source
```

That source determines the base scaling contribution.

Later grants:

```text
do not replace the primary source
```

They only add duplicate-grant bonus.

Example:

```text
Bear grants Growl first
→ Bear becomes primary source
```

---

# Duplicate Grant Rule (Already Implemented)

Each additional progression granting the same leveled ability adds:

```text
+5 effective levels
```

Example:

```text
Bear grants Growl
Berserker grants Growl
→ Growl level = 6
```

This behavior already exists and remains unchanged.

---

# Use Progression Rule (Planned)

Future model:

leveled abilities will gain additional ranks through use:

```python
character.ability_use_ranks["Ability Name"]
```

These ranks will contribute:

```text
+ use ranks
```

to effective level.

This mechanism has **not yet been implemented**.

---

# Proposed Effective Level Formula (Future Behavior)

Target model:

```text
effective level
=
primary source contribution
+ 5 × duplicate grant count
+ use ranks
```

Example:

```text
primary source level = 1
duplicate sources = 2
use ranks = 3
→ effective level = 14
```

This reflects intended behavior, not current engine output.

---

# Proposed Storage Model (Not Yet Implemented)

Discussion proposed storing:

```python
character.ability_provenance
character.ability_use_ranks
```

Example structure:

```python
character.ability_provenance["Growl"] = {
    "primary_source": ("race", "Bear"),
    "duplicate_sources": {("adventure", "Berserker")}
}
```

These fields do **not currently exist** in the engine.

They are part of a planned extension to support source-aware scaling.

---

# Proposed Scaling Guidance (Future Pattern)

Current pattern:

```python
scale_fn=lambda c: c.ability_levels.get("Growl", 0)
```

Planned replacement:

```python
scale_fn=lambda c:
    get_leveled_ability_effective_level(c, "Growl")
```

This helper does not yet exist.

---

# What This Discussion Established

This conversation defined:

```text
the intended long-term scaling model for leveled abilities
```

Specifically:

* leveled abilities should track their initial grant source
* duplicate sources should continue adding +5 each
* abilities should eventually gain ranks through use
* effective level should be derived during rebuild
* ability_levels[...] should remain the public read interface

---

# What Has NOT Changed Yet

The engine currently still uses:

```python
character.ability_levels["Ability Name"]
```

as the primary scaling source.

No changes have been made to:

```text
shared ability definition syntax
ability stacking implementation
character field layout
rebuild pipeline
content registry behavior
grant mapping logic
pattern helper usage
```

This discussion produced a **design direction**, not an implementation update.

---

# Intended Scope of Future Model

When implemented, this progression system should apply to:

```text
all leveled shared abilities
all leveled skills
all progression-granted abilities marked scales_with_level=True
```

Non-leveled abilities will remain unchanged.