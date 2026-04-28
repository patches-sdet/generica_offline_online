# Ability DSL Usage Guidelines: When to Use `apply_state(...)` vs Other Patterns

This document defines **how ability effects should be expressed using the shared ability DSL**, and clarifies the intended role of `apply_state(...)` relative to the rest of `patterns.py`.

The goal is **consistency, correctness, and maintainability** across all job ability definitions.

---

# Core Rule

Always use the **most specific truthful DSL primitive available**.

Use `apply_state(...)` **only when no higher-level effect pattern correctly represents the behavior yet**.

---

# Pattern Selection Hierarchy

Choose patterns in this order:

```
derived/stat effects
attack modifiers
skill checks
event listeners
passive runtime modifiers
resource effects
summons / creation
fallback: apply_state(...)
```

This ensures the engine remains:

* deterministic
* inspectable
* composable
* registry-friendly
* rebuild-safe

---

# When to Use `scaled_derived_buff(...)`

Use when:

* effect modifies a derived stat
* effect is passive or constant
* effect participates in rebuild()
* effect scales with job level or ability level

Examples:

```
Bard → Just That Cool
Cleric → Faith
Cultist → Servant of Darkness
Duelist → Swashbuckler's Spirit
```

Correct usage:

```
scaled_derived_buff(
    stat="cool",
    scale_fn=lambda source: progression_level(source, "adventure", "Bard"),
)
```

Avoid replacing these with `apply_state(...)`.

Derived stat changes belong in the rebuild pipeline.

---

# When to Use `modify_next_attack(...)`

Use when the ability modifies:

* damage
* attack stat
* defense stat
* riders
* targeting behavior
* weapon interaction
* attack resolution logic

Examples:

```
Holy Smite
Unholy Smite
Fancy Flourish
Disarm
Elemental Arrow variants
```

Correct usage:

```
modify_next_attack(_holy_smite_modifier)
```

Avoid encoding attack behavior inside `apply_state(...)`.

---

# When to Use `skill_check(...)`

Use when the ability:

* rolls a stat + skill
* compares against a difficulty
* applies effects on success/failure

Examples:

```
Conjuror's Eye
Cold Read
Lay of the Land
Disable Trap
Case the Joint
```

Correct usage:

```
skill_check(
    ability="Cold Read",
    stat="charisma",
    difficulty=target_willpower,
    on_success=inspect(...),
)
```

Do not replace roll-resolution logic with state placeholders.

---

# When to Use `passive_modifier(...)`

Use when the ability modifies runtime behavior of a subsystem.

Examples:

```
Weapon Specialist
Parry
Riposte
Locksmith
Gang Up
Two-Handed Specialist
```

Correct usage:

```
passive_modifier(_weapon_specialist_modifier)
```

These are not timed states. They are subsystem hooks.

---

# When to Use `on_event(...)`

Use when behavior triggers from a specific event.

Examples:

```
Power From Pain
future: on_kill
future: on_hit
future: on_crit
future: on_damage_taken
```

Correct usage:

```
on_event("damage_taken", effect)
```

Avoid encoding event triggers inside state metadata unless runtime support does not yet exist.

---

# When to Use `summon(...)` / creation patterns

Use when the ability:

* creates entities
* creates items
* conjures companions
* produces minions

Examples:

```
Summon Least
Handy Weapon
Handy Shield
Animator constructs
future Necromancer summons
```

These should not be replaced with generic state payloads unless runtime behavior is still under construction.

---

# When to Use `apply_state(...)`

Use `apply_state(...)` when:

* behavior is real but runtime execution is deferred
* ability expresses structured metadata
* effect cannot yet be represented by an existing DSL primitive
* ability describes conditional rules rather than direct stat changes
* ability modifies targeting logic indirectly
* ability establishes stance-like or aura-like conditions
* ability stores committed resources
* ability defines inspection masking or deception layers
* ability creates persistent contextual permissions

Examples:

```
Blessing
Divine Destiny
Guard Stance
Offensive Stance
Mobility Stance
Conceal Status
Darkspell
Godspell
Transfer Wounds setup
Rite of Reclamation
```

Correct usage:

```
apply_state(
    "guard_stance_active",
    value_fn=lambda source: {...}
)
```

---

# Why `apply_state(...)` Exists

`apply_state(...)` is the structured fallback between:

```
fully modeled DSL primitives
and
custom one-off Effect classes
```

It allows ability definitions to remain:

* declarative
* inspectable
* registry-safe
* deterministic
* future-runtime-compatible

without introducing premature engine complexity.

---

# What `apply_state(...)` Is NOT

`apply_state(...)` is not:

* a replacement for derived stat effects
* a replacement for attack modifiers
* a replacement for skill checks
* a replacement for event listeners
* a replacement for passive modifiers

Overusing it turns the DSL into a metadata container instead of a behavior description system.

---

# Promotion Rule: When State Payloads Become Patterns

If multiple abilities share the same state structure, promote that structure into a shared helper.

Examples already emerging:

Candidate pattern families:

```
committed_resource_buff(...)
stance(...)
summon_arcane(...)
temporary_conjured_item(...)
inspection_mask(...)
focus_target_buff(...)
```

Rule:

```
one job uses state → keep apply_state(...)
three jobs use same state → promote to pattern
```

This keeps the DSL clean and prevents premature abstraction.

---

# Design Philosophy

Preferred order of expression:

```
exact DSL primitive
→ structured helper pattern
→ apply_state(...)
→ custom Effect subclass (last resort)
```

Goal:

```
maximum clarity
minimum boilerplate
no fake precision
future runtime compatibility
```

---

# Quick Reference Decision Table

| Ability behavior               | Use                    |
| ------------------------------ | ---------------------- |
| Derived stat bonus             | scaled_derived_buff    |
| Attack modification            | modify_next_attack     |
| Roll vs difficulty             | skill_check            |
| Runtime subsystem hook         | passive_modifier       |
| Event-triggered effect         | on_event               |
| Entity creation                | summon / create_entity |
| Temporary structured condition | apply_state            |
| Future runtime placeholder     | apply_state            |

---

# Summary Rule

Use the **highest-fidelity shared DSL primitive available**.

Use `apply_state(...)` only when behavior is real but **engine execution support is not yet finalized**.

When repeated state payloads appear across multiple jobs, promote them into new shared patterns.
