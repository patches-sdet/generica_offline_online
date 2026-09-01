# Phase 3 - Creating the Typed Definitions Layer

## Goal
Replace loosely structured nested dictionaries with typed Python definition objects that are easy to read, validate, and test.

## Why this phase matters
The current builder in [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39) receives dictionaries. That is flexible, but it leaves too much room for silent shape drift and unclear authoring rules.

Typed definitions give you:
- autocomplete
- easier validation
- more readable tests
- cleaner migration path away from YAML as the primary authoring source

## Suggested objects

### Minimum useful set
- `JobDefinition`
- `AbilityDefinition`
- `ActivationSpec`
- `GrantSpec`

## Beginner-friendly example
**Example sketch — shape only**

```python
from dataclasses import dataclass, field
from typing import Literal


AbilityKind = Literal["active", "passive", "skill"]


@dataclass(frozen=True, slots=True)
class ActivationSpec:
    cost: int = 0
    cost_pool: str | None = None
    duration: str | None = None
    target: str = "self"


@dataclass(frozen=True, slots=True)
class GrantSpec:
    name: str
    required_level: int = 1


@dataclass(frozen=True, slots=True)
class AbilityDefinition:
    name: str
    kind: AbilityKind
    required_level: int
    description: str
    activation: ActivationSpec = ActivationSpec()
    scales_with_level: bool = False
    effects: tuple[object, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class JobDefinition:
    owner_type: str
    owner_name: str
    abilities: tuple[AbilityDefinition, ...]
    grants: tuple[GrantSpec, ...] = field(default_factory=tuple)
```

## How this maps to current repository behavior
- `name`, `description`, `cost`, `cost_pool`, `duration`, `target`, and `scales_with_level` already correspond closely to fields consumed in [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39).
- `required_level` corresponds to the grant-registration behavior near [`build_job()`](src/domain/abilities/builders/_job_builder.py:104).

## Design rules

### Rule 1: keep authoring objects dumb
Definition objects should mostly hold data, not execute game logic.

### Rule 2: put translation logic in the compiler
Do not hide major behavior in the dataclasses themselves.

### Rule 3: represent optional concepts explicitly
If activation is absent for a passive ability, still use a predictable shape.

### Rule 4: prefer tuples and frozen dataclasses
This makes test comparisons and accidental mutation debugging easier.

## Suggested first validation checks
When source work begins later, add validation that:
- names are non-empty
- kind is one of the allowed values
- passive definitions do not pretend to need active-only activation semantics
- effects are present when required
- required levels are positive integers

## Migration thought process
When reading [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml), ask:
- what is plain metadata?
- what is activation metadata?
- what is effect description?
- what is a grant?

Those become different typed objects instead of one giant nested mapping.

## Exit criteria for this phase
- You can describe the minimum field set of an `AbilityDefinition`.
- You can map Berserker YAML concepts into typed objects.
- You are ready to define effect-spec objects next.
