# Generica Offline Online — Stuff and Nonsense RPG Character Engine

A modular, effect-driven RPG character engine built in Python, designed for **deterministic state, composability, and long-term extensibility**.

This project started as a way to create characters using the complex rules from the LitRPG book series, Stuff and Nonsense by Andrew Seiple, but has evolved beyond a simple manager into a fully architected simulator capable of supporting resource usage, active ability usage, and potentially future combat mechanics.

---

## Core Idea

```text
state = function(all inputs)
```

All character state is **fully recomputed from source data**.
No incremental mutation. No hidden state. No stat drift.

---

## ⚙️ Key Features

* Deterministic stat pipeline
* Effect-based stat modification system
* Modular job and profession systems
* Data-driven ability system (auto-registered)
* Material-based race composition (e.g., Golem = Base Race + Material)
* Source-aware attribute tracking
* Runtime system for active abilities and resource usage
* CLI interaction loop
* JSON persistence

---

## Architecture

This project attempts to follow a hexagonal architecture style, separating domain logic from application flow and presentation.

```text
src/
├── application/      # Use-cases (character creation)
├── domain/           # Core systems (pure logic)
├── presentation/     # Read-only display
├── persistence/      # Saved character data
├── main.py           # CLI entry point
├── cli.py            # (emerging alternate interface)
```

---

## Core Systems

### Character Model

The **single source of truth** for all state:

* race (with optional base race + material)
* race level (+ future base race level support)
* adventure job + level
* profession job + level
* attributes (mutable + base snapshot)
* attribute source tracking
* derived stats (pools, defenses)
* abilities + ability levels
* runtime resource pools

---

### Effects System

All stat changes flow through:

```python
Effect.apply(character, source="...")
```

Types:

* `StatIncrease`
* `DerivedStatBonus`
* `DerivedStatOverride`

Supports:

* deterministic stacking
* source tagging (job, ability, race, etc.)
* future systems (equipment, buffs)

---

### Recalculation Engine

Core function:

```python
recalculate(character)
```

Rebuilds the character from:

```text
race → job → profession → abilities
```

Guarantees:

* no stat drift
* full reproducibility
* predictable debugging

---

### Jobs System

#### Adventure Jobs

* Define character identity
* Provide stat scaling and ability unlocks

#### Profession Jobs

* Provide steady stat growth
* Lightweight and fully composable

---

### Ability System

Fully data-driven:

* unlock conditions
* passive effects (via recalculation)
* active execution (via runtime)
* ability levels per character
* auto-registration via module loading

Supports:

```text
* passive bonuses
* resource costs (e.g., Fortune)
* custom execution logic
```

---

### Runtime System

Handles gameplay actions:

* resource spending
* ability execution
* state mutation between recalculations

Example:

```python
execute_ability(character, ability_name)
```

---

### Race System (Composite)

Supports **material-based races**:

```text
Golem = Base Race + Material
```

Example:

```text
Golem (Metal Human)
```

* base race contributes scaling
* material contributes effects
* overlay race defines identity

---

### Derived Stats

#### Pools

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
   → if required: choose base race + material
2. Choose adventure job
3. Choose profession
4. Initialize attributes
5. Recalculate
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

* race (including base + material)
* job + profession
* attributes with source breakdowns
* pools and defenses
* abilities with metadata

Example:

```text
STR: 32 (29 +2 Archer +1 Ability)
Race: Golem (Metal Human)
```

---

## Persistence

Characters are saved as JSON:

```text
src/persistence/<name>_character.json
```

---

## Current Status

```text
CORE ENGINE: STABLE
DETERMINISTIC PIPELINE: COMPLETE
EFFECT SYSTEM: UNIFIED
ABILITY SYSTEM: FUNCTIONAL
RUNTIME: ACTIVE
ATTRIBUTE TRACKING: IMPLEMENTED
```

---

## Roadmap

### Near-Term

* Loading existing character sheets
* Derived stat source tracking
* Ability scaling improvements
* Level-up system
* Equipment system (already scaffolded)

### Mid-Term

* Combat engine
* Buff/debuff system
* Turn system
* Enemy/AI models

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

## ▶️ Running the Project

```bash
./run.sh
```

or:

```bash
python src/main.py
```

---

## Why This Project Exists

Most RPG systems break under complexity due to:

* hidden state mutations
* hardcoded logic
* unclear stat origins

This engine is designed to avoid those pitfalls by making all state explicit, reproducible, and inspectable.

---

