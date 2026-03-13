# Tabletop RPG Character Manager

A Python-based, production-ready system for creating, managing, and printing characters for a crunch-heavy tabletop RPG system. This project follows Clean Architecture principles and is designed for dynamic, stat-driven gameplay.

---

## Table of Contents

- [Overview](#overview)  
- [Architecture & Design Decisions](#architecture--design-decisions)  
- [Project Structure](#project-structure)  
- [Core Components](#core-components)  
- [Character Creation Flow](#character-creation-flow)  
- [Pools & Pool Management](#pools--pool-management)  
- [Printing / Presentation](#printing--presentation)  
- [Usage Example](#usage-example)  
- [Future Work](#future-work)

---

## Overview

This project is designed to handle:

- Character creation with randomized or base stats
- Dynamic pool calculation (HP, Stamina, Sanity, Moxie, Fortune)
- Pool adjustments (damage, healing, spending, recovery)
- Colored, cleanly formatted character sheets for terminal display
- Flexible architecture suitable for expansion (new jobs, equipment, skills, etc.)

---

## Architecture & Design Decisions

- **Clean Architecture Principles:**  
  - `domain/` contains core entities and business logic (`Attributes`, `Pools`, `Character`)  
  - `application/` contains use cases (`character_creation.py`)  
  - `presentation/` handles printing and UI (`character_sheet.py`)  
  - `utils/` is reserved for generic helper functions  

- **Domain-Centric:**  
  - Pools and their management logic are part of the domain, keeping core rules centralized.  
  - Attributes and stats drive derived values like pools.

- **Extensibility:**  
  - Pools are generic and stored as `(current, max)` tuples for easy adjustments.  
  - PoolManager allows dynamic changes without hardcoding methods for each pool.  
  - Adding new pools in the future only requires modifying the `Pools` dataclass and `PRETTY_NAMES` / `POOL_COLORS` mappings.

- **Separation of Concerns:**  
  - Domain logic is separate from presentation.  
  - Calculation of max values happens in domain/application layer.  
  - Presentation only handles printing, coloring, and formatting.

---

## Project Structure

```text
├── pyproject.toml
├── README.md
├── src
│   ├── application
│   │   └── character_creation.py
│   ├── domain
│   │   ├── attributes.py       # Attributes, Pools, PoolManager, constants
│   │   ├── character.py
│   │   ├── adventure_job.py
│   │   ├── craft_job.py
│   │   ├── equipment.py
│   │   ├── race.py
│   │   └── skills.py
│   ├── main.py
│   ├── persistence
│   ├── presentation
│   │   └── character_sheet.py  # print_stat_block, debug_print_character
│   └── utils
└── tests

---

## Core Components

Attributes

- Stores all character stats: strength, constitution, intelligence, wisdom, dexterity, agility, charisma, willpower, perception, luck
- Optional character traits: race, adventuring_job, craft_job, levels
- Used to calculate derived pools dynamically

Pools
- Dataclass containing hp, sanity, stamina, moxie, fortune as (current, max) tuples
- Maximum values are dynamically calculated based on attributes
- Current values start equal to max but can be adjusted during gameplay

PoolManager

-Generic helper for all pools
- Supports:
-- adjust_pool(pool_name, delta) — dynamically adjust current value
-- get_current(pool_name) / get_max(pool_name)
-- set_current(pool_name, value) — clamps between 0 and max
-- Avoids repetitive methods for each pool
-- Enforces safe value ranges automatically

## Character Creation Flow

1. Generate Attributes
- Base value from race and dice roll
- example: (Human) Strength = 25 + 2d10

2. Calculate Pools
- Uses a pair of attributes to derive a tuple for current and max pools

3. Wrapped Pools in PoolManager
- This could be used to dynamically update pools during a session

4. Create Character
- This will generate a pretty print of the character

## Pools & Pool Management

- Pools are derived using the following formulas:

-- hp = strength + constitution
-- sanity = wisdom + intelligence
-- stamina = constitution + agility
-- moxie = charisma + willpower
-- fortune = perception + luck

- Adjusting pools uses PoolManager.adjust_pool("hp", -10)
- Printing pools uses print_stat_block("Pools", vars(character.pools), color_map=POOL_COLORS)

## Printing & Presentation

- print_stat_block(title, stats, hide_keys=None, color_map=None)
-- Handles tuples as current/max
-- Applies colors via the color_map
-- Formats them easy reference

- debug_print_character(character)
-- Prints Attributes, Pools, and Defense in an orderly format
-- Compatible with applying colors

## Usage Example

from domain.attributes import calculate_pools, PoolManager, POOL_COLORS, print_stat_block

# Generate character attributes (application/character_creation)
attrs = character.attributes

# Calculate pools dynamically
character.pools = calculate_pools(attrs)

# Wrap in generic PoolManager
pool_manager = PoolManager(character.pools)

# Adjust pools dynamically
pool_manager.adjust_pool("hp", -15)
pool_manager.adjust_pool("stamina", -5)
pool_manager.adjust_pool("moxie", +3)

# Print pools in colored format
print_stat_block(
    "Pools",
    vars(character.pools),
    color_map=POOL_COLORS
)

## Future Work

- Add buffs, debuffs, and effects that temporarily modify current or max pools
- Implement equipment bonuses that dynamically update attributes and recalc pools
- Add races, jobs, skills, and crafting systems with full integration into the character flow
- Add unit tests to verify pool calculations, adjustments, and printing
