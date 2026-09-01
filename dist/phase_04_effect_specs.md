# Phase 4 - Creating Effect Specs

## Goal
Represent ability effects as structured Python spec objects instead of opaque nested dictionaries.

## Why this phase matters
The abilities cleanup is not only about metadata. The real difficulty is the effect behavior currently embedded in nested structures like those in [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml).

If the definitions layer is the “what,” the effect-spec layer is the “what happens.”

## What good effect specs should do
- be explicit
- be composable
- stay small
- compile cleanly into current runtime behavior
- avoid pretending to solve every future gameplay mechanic immediately

## Suggested first effect-spec types
- `ModifyNextAttackSpec`
- `ApplyStateSpec`
- `OnEventSpec`
- `AttackSpec`
- `ContestSpec`
- bonus-expression helpers such as `FlatBonus`, `ProgressionLevelBonus`, and `AbilityLevelBonus`

## Example sketches
**Example sketches — shape only**

```python
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FlatBonus:
    amount: int


@dataclass(frozen=True, slots=True)
class ProgressionLevelBonus:
    source_type: str
    source_name: str
    multiplier: int = 1


@dataclass(frozen=True, slots=True)
class AbilityLevelBonus:
    ability_name: str
    multiplier: int = 1


@dataclass(frozen=True, slots=True)
class ModifyNextAttackSpec:
    damage_bonus: tuple[object, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ApplyStateSpec:
    state: str
    payload: object | None = None


@dataclass(frozen=True, slots=True)
class OnEventSpec:
    event_name: str
    effect: object
```

## Berserker mapping examples

### Furious Strike
The YAML in [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) shows a `modify_next_attack` effect with damage coming from progression level plus ability level. That is a good fit for:
- one `ModifyNextAttackSpec`
- one `ProgressionLevelBonus`
- one `AbilityLevelBonus`

### Build Up
The same file shows a stateful “apply state” concept. That is a good fit for:
- one `ApplyStateSpec`
- a structured payload object or a deliberately small dictionary payload if needed during transition

### Power From Pain
This is a useful reminder that not every event-driven case should be overgeneralized on day one. An `OnEventSpec` wrapper is enough for the pilot, even if some internals remain transitional.

## Practical advice for a beginner
Do not try to design the perfect universal effect model.

Instead, ask:
1. What effect shapes appear in Berserker?
2. Which of those can be named clearly?
3. Which need a small transition escape hatch?

That approach keeps the first version realistic.

## Exit criteria for this phase
- You can express Berserker’s major effects without giant nested dicts.
- You know which parts are strongly typed and which parts are transitional.
- You are ready to compile specs into runtime behavior.
