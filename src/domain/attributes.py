from dataclasses import dataclass, field, asdict
from typing import Callable

# BASE ATTRIBUTE DEFINITIONS

DEFAULT_STATS: dict[str, int] = {
    "strength": 25,
    "constitution": 25,
    "intelligence": 25,
    "wisdom": 25,
    "dexterity": 25,
    "agility": 25,
    "charisma": 25,
    "willpower": 25,
    "perception": 25,
    "luck": 25,
}

ATTRIBUTE_NAMES: tuple[str, ...] = tuple(DEFAULT_STATS.keys())

@dataclass(slots=True)
class Attributes:
    values: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for stat, base in DEFAULT_STATS.items():
            self.values.setdefault(stat, base)

    def add(self, stat: str, amount: int) -> None:
        self.values[stat] = self.values.get(stat, 0) + amount

    def set(self, stat: str, value: int) -> None:
        self.values[stat] = value

    def get(self, stat: str) -> int:
        return self.values.get(stat, 0)

    def reset_to_defaults(self) -> None:
        self.values = dict(DEFAULT_STATS)

    def to_dict(self) -> dict[str, int]:
        return dict(self.values)

# DERIVED STAT FORMULAS

STAT_FORMULAS: dict[str, Callable[[Attributes], int]] = {
    "hp": lambda a: a.get("strength") + a.get("constitution"),
    "sanity": lambda a: a.get("intelligence") + a.get("wisdom"),
    "stamina": lambda a: a.get("strength") + a.get("agility"),
    "moxie": lambda a: a.get("charisma") + a.get("willpower"),
    "fortune": lambda a: a.get("perception") + a.get("luck"),
}

# POOL SNAPSHOT / CALC RESULT

@dataclass(slots=True)
class Pools:
    hp: tuple[int, int]
    sanity: tuple[int, int]
    stamina: tuple[int, int]
    moxie: tuple[int, int]
    fortune: tuple[int, int]

    def to_dict(self) -> dict[str, tuple[int, int]]:
        return asdict(self)

# DEFENSES

@dataclass(slots=True)
class Defenses:
    armor: int = 0
    mental_fortitude: int = 0
    endurance: int = 0
    cool: int = 0
    fate: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

DEFENSE_KEYS: tuple[str, ...] = (
    "armor",
    "mental_fortitude",
    "endurance",
    "cool",
    "fate",
)