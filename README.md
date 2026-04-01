# 🧠 Generica Offline Online

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-in--development-orange)
![Architecture](https://img.shields.io/badge/architecture-effect--driven-success)
![License](https://img.shields.io/badge/license-MIT-green)

## A Data-Driven RPG Character Engine

A modular, effect-driven RPG engine built in Python, designed for **deterministic state, composability, and long-term extensibility**.

This project has evolved from a simple stat calculator into a **fully generic progression and simulation engine**, where all gameplay behavior is expressed through data and effects.

---

## Table of Contents

* [Core Philosophy](#-core-philosophy)
* [Architecture Overview](#-architecture-overview)
* [Getting Started](#-getting-started)
* [Project Structure](#-project-structure)
* [Calculation Pipeline](#-calculation-pipeline)
* [Progression System](#-progression-system-in-transition)
* [Key Concepts](#-key-concepts)
* [Features](#-current-features)
* [Roadmap](#-roadmap)
* [Contributing](#-contributing)
* [License](#-license)

---

# Core Philosophy

```text
Content → Abilities → Effects → Calculations → Final State
```

### Key Principle

> **Everything in the system is expressed as Effects.**

* No direct stat mutation outside the calculation pipeline
* All systems resolve into a unified effect model
* Deterministic rebuild guarantees consistency and debuggability

---

# Architecture Overview

## Effect System (Foundation)

Effects are the **single source of truth** for all gameplay logic.

### Types of Effects

* **Attribute Effects**

  * `StatIncrease`
  * `MultiStatIncrease`

* **Derived Effects**

  * `DerivedStatBonus`
  * `DerivedStatOverride`

* **Scaling Effects**

  * `ScalingEffect`

* **Runtime Effects**

  * Damage, healing, conditions

---

## Layered Stat Model

```text
Attributes → Derived Stats → Defenses / Pools
```

---

## Ability System

```python
Ability:
    name
    unlock_condition
    execute OR effect_generator
    flags (is_passive, is_skill)
```

---

## Ability Registry

* Central `_ABILITY_REGISTRY`
* Populated via `make_ability()`
* Auto-loaded via dynamic imports

---

## Job Builder (Content Compiler)

```python
build_job(job_name, definitions)
```

Transforms structured definitions into fully wired abilities.

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/generica-offline-online.git
cd generica-offline-online
```

## 2. Install Requirements

```bash
pip install -r requirements.txt
```

## 3. Run the Engine

```bash
python main.py
```

---

## Example: Creating a Character

```python
from application.character_creation import create_character

character = create_character(
    name="Test",
    race="Human",
    jobs=[("Warrior", 5)],
    professions=[("Blacksmith", 3)]
)

character.recalculate()

print(character.defenses.fate)
```

---

# Project Structure

```text
abilities/
  definitions/     # Adventure jobs
  professions/
  races/
  advanced/

domain/
application/
presentation/
```

---

# Calculation Pipeline

```python
def recalculate(character):
    reset_derived()
    rebuild_abilities(character)
    rebuild_skills(character)
    effects = collect_effects(character)
    rebuild_attributes(character, effects)
    apply_derived_effects(character, effects)
    calculate_pools(character)
    calculate_defenses(character)
    rebuild_tags(character, effects)
    return character
```

---

# Progression System (In Transition)

## New Model

```python
@dataclass
class Progression:
    name: str
    type: str
    level: int
```

## End Goal

```text
Character = base state + progressions
```

---

# Key Concepts

## Effect Contract

> All ability outputs MUST resolve to a flat `List[Effect]`

---

## Static vs Runtime Effects

* Static: race, jobs, professions, equipment
* Runtime: temporary, event-driven

---

## Deterministic Simulation

```text
base state + effects → final state
```

---

# Current Features

* Effect system
* Ability registry
* Passive & active abilities
* Skill system
* Job builder DSL
* Content generator

---

# Roadmap

* Complete progression unification
* Remove legacy level systems
* Generic `collect_effects()`
* Expand content library

---

# Contributing

Contributions are welcome!

### Guidelines

* Follow the effect-driven architecture
* Ensure all abilities return `List[Effect]`
* Keep systems data-driven

---

# License

This project is licensed under the MIT License.