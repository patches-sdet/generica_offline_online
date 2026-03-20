# Generica Offline Online — RPG Character Engine

A Python-based, modular RPG character engine built for **deterministic state, extensibility, and system-driven gameplay**.

This project has evolved from a character manager into a **fully architected stat engine** capable of supporting complex RPG systems including jobs, professions, abilities, and future combat mechanics.

---

## Table of Contents

* [Overview](#overview)
* [Core Design Philosophy](#core-design-philosophy)
* [Architecture](#architecture)
* [Project Structure](#project-structure)
* [Core Systems](#core-systems)
* [Character Creation Flow](#character-creation-flow)
* [Recalculation Pipeline](#recalculation-pipeline)
* [Abilities System](#abilities-system)
* [Presentation Layer](#presentation-layer)
* [Usage Example](#usage-example)
* [Current Status](#current-status)
* [Next Steps](#next-steps)

---

## Overview

This engine is designed to support:

* Modular character creation (race, jobs, professions)
* Deterministic stat calculation (no drift, no hidden mutations)
* Effect-driven stat modification
* Derived stat systems (pools and defenses)
* Passive ability system with scaling
* Clean CLI-based character sheet output
* JSON serialization for persistence

---

## Core Design Philosophy

### Deterministic State

```text
state = function(all inputs)
```

All character stats are **fully recomputed**, not incrementally mutated.

---

### Composition Over Hardcoding

Everything is expressed as:

```text
effects, not fields
```

* No hardcoded stat bonuses
* All systems plug into a shared pipeline

---

### Separation of Concerns

```text
Character     → state container
Effects       → stat mutation
Calculations  → derived values
Abilities     → conditional logic + scaling
Presentation  → read-only display
```

---

### Extensibility

New systems can be added without rewriting core logic:

* equipment
* buffs/debuffs
* active abilities
* combat systems

---

## Architecture

```text
src/
├── application/
│   └── character_creation.py
│
├── domain/
│   ├── character.py
│   ├── attributes.py
│   ├── race.py
│   ├── adventure.py
│   ├── profession.py
│   ├── effects.py
│   ├── abilities.py
│   ├── leveling.py
│   ├── calculations.py
│
├── presentation/
│   └── character_sheet.py
│
├── persistence/
│   └── *.json
│
└── main.py
```

---

## Core Systems

### Character Model

Single source of truth for all runtime state:

* race + race level
* adventure job + level
* profession job + level
* attributes (mutable)
* current pools
* derived stat modifiers
* abilities + ability levels
* base attribute snapshot (for debugging)

---

### Effects System

Unified stat modification layer:

```python
Effect.apply(character)
```

Implemented types:

* `StatIncrease`
* `DerivedStatBonus`
* `DerivedStatOverride`

---

### Jobs System

#### Adventure Jobs

* Define character role and scaling
* Provide stat bonuses and ability unlock conditions

#### Profession Jobs

* Provide steady stat growth per level
* Lightweight and fully integrated into recalculation

---

### Derived Stats

#### Pools

Calculated from attributes:

```text
hp        = STR + CON
sanity    = WIS + INT
stamina   = CON + AGI
moxie     = CHA + WIL
fortune   = PER + LUK
```

Stored as:

```text
(current, max)
```

---

#### Defenses

Do **not** depend on attributes:

```text
final = (override if exists else 0) + bonus
```

---

## Character Creation Flow

1. Select race (and optional material/template)
2. Select adventure job → level set to 1
3. Select profession job → level set to 1
4. Initialize attributes
5. Run `recalculate(character)`
6. Output character sheet

---

## Recalculation Pipeline

Core engine function:

```python
recalculate(character)
```

Rebuilds the character from:

* race effects
* job effects
* profession effects
* ability effects

---

### Pipeline Order

```text
1. Reset derived state
2. Apply race effects
3. Apply job effects
4. Apply profession effects
5. Capture base attributes
6. Unlock abilities
7. Apply passive abilities
```

---

## Abilities System

### Features

* Data-defined abilities
* Unlock conditions
* Per-character ability levels
* Passive ability execution
* Fully integrated into recalculation

---

### Example Ability

**Creator's Guardians**

```text
Enhances all non-zero attributes based on:
(WILL + ability level) // 10
```

---

### Ability Model

```python
Ability
├── name
├── unlock_condition(character)
├── effects (future expansion)
```

Character stores:

```python
abilities: List[Ability]
ability_levels: Dict[str, int]
```

---

## Presentation Layer

### Character Sheet Output

Displays:

* race + level
* jobs + levels
* attributes
* pools (colored)
* defenses
* abilities with levels

---

### Attribute Debugging (NEW)

Attributes now show base vs modified values:

```text
STR: 32 (29 +3)
```

---

## Usage Example

```python
from domain.calculations import recalculate
from presentation.character_sheet import debug_print_character

character = create_character()

recalculate(character)

debug_print_character(character)
```

---

## Current Status

```text
CORE ENGINE: COMPLETE
JOB SYSTEMS: COMPLETE
PROFESSION SYSTEM: COMPLETE
ABILITY SYSTEM: FUNCTIONAL
DETERMINISTIC PIPELINE: STABLE
DEBUG VISIBILITY: STRONG
```

---

## Next Steps

### Immediate Objective

Improve attribute visibility by breaking down stat sources:

```text
STR: 32 (29 +2 job +1 ability)
```

This requires:

* tracking stat contributions by source
* extending the effect system to tag origins
* updating the character sheet to display breakdowns

---

### Future Work

* AbilityEffect system (remove hardcoded ability logic)
* Active abilities and combat hooks
* Equipment system
* Buff/debuff system
* Multi-classing support
* Balance tuning tools
* Unit tests for deterministic validation

---

