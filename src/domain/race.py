import copy
from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class Race:
    name: str
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    racial_hp_bonus: int = 0
    racial_armor: int = 0
    racial_mental_fortitude: int = 0
    racial_endurance: int = 0
    racial_cool: int = 0
    racial_fate: int = 0

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

def make_stats(**overrides):
    stats = DEFAULT_STATS.copy()
    stats.update(overrides)
    return stats

def make_mods(**mods):
    return mods

RACES = {
        "Human": Race(
            name="Human",
            stat_modifiers=make_mods(),
        ),
        "Dwarf": Race(
            name="Dwarf",
            stat_modifiers=make_mods(
            strength = 10,
            constitution =  10,
            intelligence = -10,
            wisdom = 10,
            agility = -10,
            charisma = -10,
            willpower = 10,
            perception = -10,
            )
        ),
        "Frosted Giant": Race(
            name="Frosted Giant",
            stat_modifiers = make_mods(
            strength =35,
            constitution = 55,
            intelligence = -15,
            wisdom = -10,
            dexterity = -15,
            agility = -15,
            charisma = -10,
            willpower = -5,
            perception = -15,
            luck = -5,
        ),
        racial_armor=15,
        racial_endurance=25,
        racial_cool=10,
        )

        }

def get_race(name: str) -> Race:
    if name not in RACES:
        raise ValueError(f"Race '{name}' not defined")
    return copy.deepcopy(RACES[name])
