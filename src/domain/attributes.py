from dataclasses import dataclass
from typing import Tuple, Dict

# Default Attributes

DEFAULT_STATS = {
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

# Core Attributes

@dataclass
class Attributes:
    strength: int
    constitution: int
    intelligence: int
    wisdom: int
    dexterity: int
    agility: int
    charisma: int
    willpower: int
    perception: int
    luck: int

    def to_dict(self):
        return vars(self)

# Derived Stats

STAT_FORMULAS = {
    "hp": lambda a: a.strength + a.constitution,
    "sanity": lambda a: a.intelligence + a.wisdom,
    "stamina": lambda a: a.strength + a.agility,
    "moxie": lambda a: a.charisma + a.willpower,
    "fortune": lambda a: a.perception + a.luck,
}

@dataclass
class Pools:
    hp: Tuple[int, int]
    sanity: Tuple[int, int]
    stamina: Tuple[int, int]
    moxie: Tuple[int, int]
    fortune: Tuple[int, int]

    def to_dict(self):
        return vars(self)

