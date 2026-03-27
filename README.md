# Generica Offline Online — Stuff and Nonsense RPG Character Engine

A modular, effect-driven RPG character engine built in Python, designed for **deterministic state, composability, and long-term extensibility**.

Originally inspired by the LitRPG series *Stuff and Nonsense* by Andrew Seiple, this project has evolved into a **fully architected simulation engine** capable of supporting character progression, resource systems, active abilities, and future combat mechanics.

---

## Core Idea

```text
state = function(all inputs)
```

All character state is:

* **Fully recomputed from source data**
* **Free of incremental mutation**
* **Deterministic and reproducible**

> No hidden state. No stat drift. No ambiguity.

---

## ⚙️ Key Features

* Deterministic stat pipeline (full rebuild on demand)
* Effect-based stat modification system
* Modular job and profession systems
* Data-driven ability system (auto-registered)
* Composite race system (Base Race + Material)
* Source-aware attribute tracking
* Runtime system for active abilities and resource usage
* CLI interaction loop
* JSON persistence

---

## Architecture

This project loosely follows **hexagonal architecture**, separating pure domain logic from application flow and presentation.

```text
src/
├── application/      # Use-cases (character creation, orchestration)
├── domain/           # Core systems (pure logic)
├── presentation/     # Read-only display (character sheet)
├── persistence/      # Save/load logic
├── main.py           # CLI entry point
├── cli.py            # (emerging alternate interface)
```

---

## Deterministic Rebuild Pipeline

All character state is rebuilt through a fixed pipeline:

```text
1. Attributes (apply all effects)
2. Derived stats (bonuses + overrides)
3. Resource pools
4. Defenses
5. Tags
6. Abilities (resolved/unlocked)
7. Skills (derived)
```

```text
All stages operate on a fresh rebuild so there should be no incremental mutation between runs.
```

### Guarantees

* No stat drift
* Fully reproducible characters
* Predictable debugging
* Order-independent correctness (within stages)

---

## Core Systems

---

### Character Model

The **single source of truth** for all state:

* Race (with optional base race + material)
* Adventure job + level
* Profession job + level
* Attributes (rebuilt every cycle)
* Attribute source tracking
* Derived stats (bonuses, overrides, pools, defenses)
* Tags (aggregated)
* Abilities (resolved dynamically)
* Skills (derived from abilities)
* Resource pools (current/max)

---

### Effects System

All state changes flow through effects:

```python
effect.apply(EffectContext(source, targets))
```

#### Core Effect Types

* `StatIncrease`
* `MultiStatIncrease`
* `DerivedStatBonus`
* `DerivedStatOverride`

#### Principles

* Effects are **declarative**
* Effects describe **what happens**, not *when*
* Fully composable and source-aware

```text
Effects = declarative state transformations  
Calculations = deterministic orchestration pipeline
```

---

### Recalculation Engine

Central orchestration:

```python
recalculate(character)
```

Rebuilds state from:

```text
race → jobs → professions → abilities → derived systems
```

---

### Jobs System

#### Adventure Jobs

* Define character identity
* Provide stat scaling
* Unlock abilities

#### Profession Jobs

* Provide steady stat growth
* Fully composable
* Built from structured data

---

### Ability System

Data-driven and extensible:

* Passive effects (applied during recalculation)
* Active execution (via runtime)
* Unlock conditions
* Ability levels per character
* Auto-registration via module loading

#### Current Direction

```text
Ability → Effects + Targeting + Conditions → Runtime executes
```

Supports:

* Passive bonuses
* Resource costs (e.g., Fortune)
* Event-driven extensions (future)

---

### Runtime System

Handles gameplay actions outside recalculation:

* Ability execution
* Resource spending
* Temporary state changes

```python
execute_ability(character, ability_name)
```

> The runtime is evolving toward a **stateless executor of effects**, not a holder of game logic.

---

### Race System (Composite)

Supports layered race construction:

```text
Golem = Base Race + Material
```

Example:

```text
Golem (Metal Human)
```

* Base race provides scaling
* Material provides modifiers
* Composite defines identity

---

### Derived Stats

#### Resource Pools

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

```text
final = (override or 0) + bonus
```

---

## Character Creation Flow

```text
1. Choose race
   → if applicable: choose base race + material
2. Choose adventure job
3. Choose profession
4. Initialize attributes
5. Recalculate (full rebuild)
6. Enter interaction loop
```

---

## Interaction Loop

Players can:

```text
1. Use ability
2. Refresh character (recalculate)
3. Save & exit
4. Exit without saving
```

---

## Presentation Layer

The character sheet displays:

* Race (including composition)
* Job + profession
* Attributes with source breakdowns
* Resource pools and defenses
* Abilities with metadata

Example:

```text
STR: 32 (29 base +2 Archer +1 Ability)
Race: Golem (Metal Human)
```

---

## Persistence

Characters are stored as JSON:

```text
src/persistence/<name>_character.json
```

---

## Current Status

```text
CORE ENGINE: STABLE
DETERMINISTIC PIPELINE: COMPLETE
EFFECT SYSTEM: UNIFIED
ABILITY SYSTEM: PARTIALLY DECLARATIVE (IN TRANSITION)
RUNTIME: FUNCTIONAL
ATTRIBUTE TRACKING: IMPLEMENTED
```

---

## Roadmap

### Near-Term

* Load existing character sheets
* Derived stat source tracking
* Ability scaling improvements
* Level-up system
* Equipment system (scaffolded)

### Mid-Term

* Combat engine
* Buff/debuff system
* Turn system
* Enemy + AI models

### Long-Term

* GUI or web frontend
* Multiplayer synchronization
* Modding support (external data definitions)

---

## Design Principles

* **Determinism first**
* **Effects over mutation**
* **Composition over inheritance**
* **Separation of concerns**
* **Systems over hardcoding**

---

## Running the Project

```bash
./run.sh
```

or:

```bash
python src/main.py
```

---

## Why This Project Exists

Most RPG systems fail at scale due to:

* Hidden state mutations
* Hardcoded logic
* Untraceable stat origins

This engine avoids those pitfalls by making all state:

* **Explicit**
* **Rebuildable**
* **Inspectable**

---
