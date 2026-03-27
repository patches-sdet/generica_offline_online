from dataclasses import dataclass, field
from typing import Dict, Tuple

# =========================================================
# BASE ATTRIBUTE DEFINITIONS
# =========================================================

DEFAULT_STATS: Dict[str, int] = {
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

ATTRIBUTE_NAMES = list(DEFAULT_STATS.keys())


# =========================================================
# ATTRIBUTES CONTAINER (DYNAMIC)
# =========================================================

@dataclass
class Attributes:
    values: Dict[str, int] = field(default_factory=dict)

    # -------------------------
    # INIT
    # -------------------------

    def __post_init__(self):
        # Initialize missing stats from defaults
        for stat, base in DEFAULT_STATS.items():
            self.values.setdefault(stat, base)

    # -------------------------
    # CORE INTERFACE
    # -------------------------

    def add(self, stat: str, amount: int):
        self.values[stat] = self.values.get(stat, 0) + amount

    def set(self, stat: str, value: int):
        self.values[stat] = value

    def get(self, stat: str) -> int:
        return self.values.get(stat, 0)

    # -------------------------
    # DEBUG / DISPLAY
    # -------------------------

    def to_dict(self):
        return dict(self.values)


# =========================================================
# DERIVED STAT FORMULAS
# =========================================================

STAT_FORMULAS = {
    "hp": lambda a: a.get("strength") + a.get("constitution"),
    "sanity": lambda a: a.get("intelligence") + a.get("wisdom"),
    "stamina": lambda a: a.get("strength") + a.get("agility"),
    "moxie": lambda a: a.get("charisma") + a.get("willpower"),
    "fortune": lambda a: a.get("perception") + a.get("luck"),
}


# =========================================================
# RESOURCE POOLS
# =========================================================

@dataclass
class Pools:
    hp: Tuple[int, int]
    sanity: Tuple[int, int]
    stamina: Tuple[int, int]
    moxie: Tuple[int, int]
    fortune: Tuple[int, int]

    def to_dict(self):
        return vars(self)


# =========================================================
# DEFENSES
# =========================================================

@dataclass
class Defenses:
    armor: int = 0
    mental_fortitude: int = 0
    endurance: int = 0
    cool: int = 0
    fate: int = 0

    def to_dict(self):
        return vars(self)

DEFENSE_KEYS = [
        "armor",
        "mental_fortitude",
        "endurance",
        "cool",
        "fate",
        ]
