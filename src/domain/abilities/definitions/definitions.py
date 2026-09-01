from dataclasses import dataclass, field
from typing import Literal

AbilityKind = Literal[
    "passive",
    "skill"
]

@dataclass(frozen=True, slots=True)
class ActivationSpec:
    cost: int = 0
    cost_pool: str | None = None
    duration: str | None = None
    target: str = "self"

@dataclass(frozen=True, slots=True)
class AbilityGrant:
    name: str
    required_level: int = 1

@dataclass(frozen=True, slots=True)
class AbilityDefinition:
    name: str
    kind: AbilityKind
    required_level: int
    description: str
    activation: ActivationSpec = ActivationSpec()
    is_spell: bool = False
    scales_with_level: bool = False
    effects: tuple[object, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class JobDefinition:
    owner_type: str
    owner_name: str
    abilities: tuple[AbilityDefinition, ...]
    grants: tuple[AbilityGrant, ...] = field(default_factory=tuple)