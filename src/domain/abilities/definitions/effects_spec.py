from dataclasses import dataclass, field
from typing import Literal

PassiveScope = Literal[
    "attack",
    "defense",
    "skill_roll",
    "movement",
    "pool",
    "weapon_use"
]

PassiveModifierKey = Literal[
    "attack_bonus",
    "damage_bonus",
    "armor_bonus",
    "pool_cost",
    "roll_bonus"
]

RelativeSize = Literal[
    "smaller",
    "equal",
    "larger"
]

@dataclass(frozen=True, slots=True)
class AbilityLevelBonus:
    ability_name: str
    multiplier: int = 1

@dataclass(frozen=True, slots=True)
class ApplyStateSpec:
    state: str
    payload: object | None = None

@dataclass(frozen=True, slots=True)
class DerivedStatBuffSpec:
    stat: str | None = None
    amount: tuple[object, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class FlatBonus:
    amount: int = 0

@dataclass(frozen=True, slots=True)
class GrantSpec:
    name = str
    required_level: int

@dataclass(frozen=True, slots=True)
class ModifyNextAttackSpec:
    attack_bonus: tuple[object, ...] = field(default_factory=tuple)
    damage_bonus: tuple[object, ...] = field(default_factory=tuple)
    ignore_armor: int | tuple[object, ...] = 0
    ignore_cover: bool = False
    relative_target_size: RelativeSize | None = None
    targets_all_adjacent_enemies: bool = False
    single_roll_against_all_targets: bool = False

@dataclass(frozen=True, slots=True)
class OnEventSpec:
    event_name: str
    effect: object
    condition: object | None = None

@dataclass(frozen=True, slots=True)
class PassiveContextModifierSpec:
    applies_to: PassiveScope
    modifier: PassiveModifierKey
    value: tuple[object, ...] = field(default_factory=tuple)
    requirements: tuple[object, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class PoolCostModifierSpec:
    pool: str
    amount: int | tuple[object, ...]
    scaling_basis: str | None = None
    per_target: bool = False
    target_scope: str | None = None

@dataclass(frozen=True, slots=True)
class ProgressionLevelBonus:
    source_type: str
    source_name: str
    multiplier: int = 1

@dataclass(frozen=True, slots=True)
class WeaponRequirementSpec:
    style: str | None = None
    wielding_mode: str | None = None
