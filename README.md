# Generica Offline Online

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
* [Active Program Documents](#-active-program-documents)
* [Getting Started](#-getting-started)
* [Known-Good Workflow](#-known-good-workflow)
* [Project Structure](#-project-structure)
* [Calculation Pipeline](#-calculation-pipeline)
* [Progression System](#-progression-system-in-transition)
* [Key Concepts](#-key-concepts)
* [Features](#-current-features)
* [Roadmap](#-roadmap)
* [Contributing](#-contributing)
* [License](#-license)

---

# Active Program Documents

Contributors working on the phased restart program should treat the following documentation surfaces as the active record:

- [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) is the living roadmap, current status, practical backlog, and Phase record.
- [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md) is the governing decision record for the baseline path and deterministic-versus-runtime boundary.
- [`dist/compiled_update.md`](dist/compiled_update.md) is the reconciled baseline analysis that the current phased plan was derived from.

The retained [`dist/`](dist) document set is intentionally small. If a planning or status statement conflicts with [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md), treat [`dist/PROGRAM_STATUS.md`](dist/PROGRAM_STATUS.md) as the living source of truth.

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

## 2. Create the Development Environment

This repository is currently managed as a uv development workspace through [`pyproject.toml`](pyproject.toml:1). It is not configured as an installable package yet.

```bash
uv sync --dev
```

This installs the runtime dependency declared in [`pyproject.toml`](pyproject.toml:1) plus the development tools used by the repository, including `pytest`, `pytest-cov`, `black`, `isort`, and `ruff`.

## 3. Run the Engine

Primary entrypoint:

```bash
uv run python src/main.py
```

Shell wrapper:

```bash
./run.sh
```

The shell wrapper in [`run.sh`](run.sh:1) also exposes the job scaffolding helpers used by [`src/tools/job_generator.py`](src/tools/job_generator.py:1):

```bash
./run.sh new-job Berserker
./run.sh new-profession Brewer
./run.sh new-advanced Ranger
```

## 4. Run Tests

```bash
uv run pytest
```

Useful subsets:

```bash
uv run pytest tests/smoke -q
uv run pytest tests/regression -q
uv run pytest tests/unit -q
uv run pytest tests/blackbox -q
```

## 5. Run the narrow [`recalculate()`](src/domain/calculations/__init__.py:20) benchmark

Repo-integrated command path:

```bash
./run.sh benchmark-recalculate
```

Direct [`uv`](pyproject.toml:40) workflow:

```bash
uv run python src/tools/recalculate_benchmark.py
```

Optional JSON output for recording or diffing local runs:

```bash
uv run python src/tools/recalculate_benchmark.py --output-json
```

CI also runs the same benchmark command through [`.github/workflows/test.yml`](.github/workflows/test.yml:1) and uploads a `recalculate-benchmark` artifact containing markdown and JSON benchmark reports for each workflow run.

Benchmark interpretation:
- **Cold run**: first standalone [`recalculate()`](src/domain/calculations/__init__.py:20) call on a freshly created fixture after forced registry initialization.
- **Warm run**: repeated [`recalculate()`](src/domain/calculations/__init__.py:20) calls on an already-built fixture with registries already initialized.
- Fixture construction uses [`create_character()`](src/application/character_creation.py:170) with deterministic creation rolls patched to an empty list so runs stay reproducible in-repo.

The current benchmark harness lives in [`src/tools/recalculate_benchmark.py`](src/tools/recalculate_benchmark.py:1) and intentionally stays narrow: it measures only representative deterministic rebuild scenarios, not the broader runtime workflow.

The active test configuration lives in [`pytest.ini`](pytest.ini:1), and CI currently runs both the test matrix and the non-blocking benchmark artifact publication path through [`.github/workflows/test.yml`](.github/workflows/test.yml:1).

---

## Example: Creating a Character

```python
from application.character_creation import create_character
from domain.content_registry import initialize_content_registries

initialize_content_registries()

character = create_character(
    name="Test",
    base_race_names=["Human"],
    adventure_job_names=["Berserker"],
    profession_job_names=["Smith"],
)

print(character.defenses.fate)
```

For restart-oriented workflows, the usual path is:

```text
initialize_content_registries() → create_character() → recalculate()
```

The deterministic rebuild pipeline is implemented by [`recalculate()`](src/domain/calculations/__init__.py:18).


---

# Known-Good Workflow

Use this sequence when you want the current, restart-safe path through the codebase without making assumptions about unresolved architecture details.

## 1. Initialize registries

Call [`initialize_content_registries()`](src/domain/content_registry.py:257) before relying on races, jobs, professions, or registered abilities.

What it does:
- registers base races and race templates
- registers adventure, profession, and advanced jobs
- imports ability modules through the canonical startup hook

## 2. Create a character through the application API

Use [`create_character()`](src/application/character_creation.py:170) as the normal entrypoint for building a character from content definitions.

This API:
- validates race and template combinations
- validates adventure and profession job limits
- seeds base state
- performs an initial deterministic rebuild
- initializes current resources to their max values

## 3. Recalculate after state changes

Use [`recalculate()`](src/domain/calculations/__init__.py:18) after changes that affect derived character state.

The current deterministic rebuild order is:

```text
reset_derived
→ rebuild_skills
→ rebuild_abilities
→ collect_effects
→ rebuild_attributes
→ apply_derived_effects
→ calculate_pools
→ calculate_defenses
→ rebuild_tags
```

## 4. Use the audit path when validating content coverage

Use [`run_full_job_ability_audit()`](src/startup.py:205) when you want a repository-level validation pass over progression-to-ability grant coverage.

This is useful for restart and verification work, but it is not the normal character runtime entrypoint.

## Canonical rebuild-path note

The currently wired deterministic rebuild path flows through [`recalculate()`](src/domain/calculations/__init__.py:20), which imports and executes [`rebuild_abilities()`](src/domain/calculations/abilities.py:4). The broader baseline-path and product-boundary guidance is governed by [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md). Contributors should distinguish between:

- **intended authority after migration:** [`rebuild_abilities()`](src/application/runtime.py:318)
- **current live rebuild hook:** [`rebuild_abilities()`](src/domain/calculations/abilities.py:4) via [`recalculate()`](src/domain/calculations/__init__.py:20)

Documentation and implementation work should preserve that distinction explicitly rather than treating the two paths as equivalent.


---

# Project Structure

```text
src/
  application/   # character creation, leveling, runtime actions
  domain/        # core models, registries, calculations, effects
  presentation/  # terminal-facing character sheet output
  tools/         # content scaffolding helpers
tests/
  smoke/
  regression/
  unit/
  blackbox/
```

---

# Calculation Pipeline

```python
def recalculate(character):
    reset_derived()
    rebuild_skills(character)
    rebuild_abilities(character)
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
