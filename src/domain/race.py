import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from domain.effects import StatIncrease, Effect

@dataclass(frozen=True)
class Race:
    name: str
    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)
    racial_hp_bonus: int = 0
    racial_armor: int = 0
    racial_mental_fortitude: int = 0
    racial_endurance: int = 0
    racial_cool: int = 0
    racial_fate: int = 0
    requires_material: bool = False
    
    # Added this to allow Doll Haunters or Toy Golems
    material: Optional[str] = None
    base_race: Optional[str] = None

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "racial_hp_bonus": self.racial_hp_bonus,
            "racial_armor": self.racial_armor,
            "racial_mental_fortitude": self.racial_mental_fortitude,
            "racial_endurance": self.racial_endurance,
            "racial_cool": self.racial_cool,
            "racial_fate": self.racial_fate,
            "requires_material": self.requires_material,
            "material": self.material,
            "base_race": self.base_race,
        }

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

def make_effects(**mods):
    return [StatIncrease(stat, value) for stat, value in mods.items()]

RACES = {
        "Human": Race(
            name="Human",
            effects_on_acquire = make_effects(),
        ),
        "Dwarf": Race(
            name="Dwarf",
            effects_on_acquire = make_effects(
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
            effects_on_acquire = make_effects(
            strength = 35,
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
        racial_armor = 15,
        racial_endurance = 25,
        racial_cool = 10,
        ),
        "Gribbit": Race(
            name="Gribbit",
            effects_on_acquire = make_effects(
            constitution = 10,
            intelligence = -10,
            wisdom = 5,
            dexterity = -10,
            agility = 15,
            charisma = -5,
            willpower = -5,
            perception = 5,
            luck = -5,
        ),
        racial_armor = 5,
        racial_mental_fortitude = 10,
        racial_endurance = 5,
        ),
        "Raccant": Race(
            name="Raccant",
            effects_on_acquire = make_effects(
            strength = -15,
            constitution = 15,
            intelligence = -5,
            wisdom = -10,
            dexterity = 15,
            agility = 15,
            willpower = -15,
            perception = -5,
            luck = 5,
        ),
        racial_armor = 10,
        racial_endurance = 10,
        ),
        "Elf": Race(
            name="Elf",
            effects_on_acquire = make_effects(
            strength = 5,
            constitution = 5,
            intelligence = 5,
            wisdom = 5,
            dexterity = 5,
            agility = 5,
            willpower = 5,
            perception = 5,
            luck = 5,
        ),
        ),
        "Halven": Race(
            name="Halven",
            effects_on_acquire = make_effects(
            strength = -10,
            constitution = -10,
            intelligence = -10,
            wisdom = 10,
            dexterity = 10,
            agility = 10,
            willpower = -10,
            perception = -10,
            luck = 10,
        ),
        ),



        # Template Races (Doll Haunter, Toy Golem)
        "Toy Golem": Race(
            name="Toy Golem",
            base_race = "Human", #hardcoded for initial testing, this can probably be deleted
            effects_on_acquire = make_effects(),
        racial_hp_bonus = 30,
        racial_cool = 20,
        requires_material = True,
        ),
        "Doll Haunter": Race(
            name="Doll Haunter",
            effects_on_acquire = make_effects(),
        racial_hp_bonus = 30,
        racial_cool = 20,
        requires_material = True,
        ),
        }

def get_race(name: str) -> Race:
    if name not in RACES:
        raise ValueError(f"Race '{name}' not defined")
    return copy.deepcopy(RACES[name])

def resolve_race(race_name: str) -> Race:
    """
    Resolve a race including any base race inheritance.
    """

    race = get_race(race_name)

    if not race.base_race:
        return race

    base = resolve_race(race.base_race)

    # Merge stats
    combined_modifiers = {
        stat: base.stat_modifiers.get(stat, 0) + race.stat_modifiers.get(stat, 0)
        for stat in set(base.stat_modifiers) | set(race.stat_modifiers)
    }

    return Race(
        name=race.name,
        effects_on_acquire=combined_modifiers,

        requires_material=race.requires_material,
        racial_hp_bonus=base.racial_hp_bonus + race.racial_hp_bonus,
        racial_armor=base.racial_armor + race.racial_armor,
        racial_mental_fortitude=base.racial_mental_fortitude + race.racial_mental_fortitude,
        racial_endurance=base.racial_endurance + race.racial_endurance,
        racial_cool=base.racial_cool + race.racial_cool,
        racial_fate=base.racial_fate + race.racial_fate
    )

def apply_material_template(race: Race, material: str) -> Race:
    """
    Apply the material-based modifiers to Doll Haunters and Toy Golems.
    """

    MATERIALS = {
            "cloth": {
                "armor": 10,
                "endurance": 20
                },
            "leather": {
                "armor": 15,
                "endurance": 15
                },
            "metal": {
                "armor": 20,
                "endurance": 10
                }
            }

    if material not in MATERIALS:
        raise ValueError(f"Invalid Material: {material}. Choose from {MATERIALS}")

    mod = MATERIALS[material]

    return Race(
            name = race.name,
            effects_on_acquire = race.effects_on_acquire.copy(),

            material=material,
            requires_material=False,

            racial_hp_bonus = race.racial_hp_bonus,
            racial_armor = race.racial_armor + mod["armor"],
            racial_mental_fortitude = race.racial_mental_fortitude,
            racial_endurance = race.racial_endurance + mod["endurance"],
            racial_cool = race.racial_cool,
            racial_fate = race.racial_fate,
        )

