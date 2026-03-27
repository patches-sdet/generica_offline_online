import copy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease, MultiStatIncrease, DerivedStatBonus, DerivedStatOverride


# =========================================================
# CORE RACE MODEL
# =========================================================

@dataclass(frozen=True)
class Race:
    name: str

    # Effects
    effects_on_acquire: Tuple[Effect] = field(default_factory=list)
    effects_per_level: Tuple[Effect] = field(default_factory=list)

    # Tags
    tags: Tuple[str] = field(default_factory=list)

    # Limits
    max_adventure_jobs: int = 1
    max_profession_jobs: int = 1

    # Material system
    requires_material: bool = False
    material: Optional[str] = None
    can_be_base: bool = True
    base_race: Optional[str] = None
    
    def get_effects(self, level: int):
        level = max(1, level)

        effects = []
        effects.extend(self.effects_on_acquire or [])
        effects.extend(self.effects_per_level * max(0, level - 1))

        return effects


    # -------------------------
    # DISPLAY
    # -------------------------

    def get_display_name(self) -> str:
        if self.base_race and self.material:
            return f"{self.name} ({self.material.title()} {self.base_race})"
        elif self.material:
            return f"{self.name} ({self.material.title()})"
        return self.name

    # -------------------------
    # SERIALIZATION
    # -------------------------

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "tags": self.tags,
            "requires_material": self.requires_material,
            "material": self.material,
            "base_race": self.base_race,
        }


# =========================================================
# HELPERS
# =========================================================

def make_effects(**mods):
    return [StatIncrease(stat, value) for stat, value in mods.items()]


# =========================================================
# RACE DEFINITIONS
# =========================================================

RACES = {
    "Doll Haunter": Race(
        name="Doll Haunter",
        requires_material=True,
        can_be_base=False,
        tags=["construct"],
    ),

    "Dwarf": Race(
        name="Dwarf",
        effects_on_acquire=[MultiStatIncrease(
            {
                "strength": 10,
                "constitution": 10,
                "intelligence": -10,
                "wisdom": 10,
                "agility": -10,
                "charisma": -10,
                "willpower": 10,
                "perception": -10,
                }
        )
                            ],
        max_adventure_jobs=5,
        max_profession_jobs=5,
        tags=["humanoid"],
    ),

    "Elf": Race(
        name="Elf",
        effects_on_acquire=[MultiStatIncrease(
            {
                "strength": 5,
                "constitution": 5,
                "intelligence": 5,
                "wisdom": 5,
                "dexterity": 5,
                "agility": 5,
                "willpower": 5,
                "perception": 5,
                "luck": 5,
                }
        )
                            ],
        tags=["humanoid"],
    ),

    "Frosted Giant": Race(
        name="Frosted Giant",
        effects_on_acquire=[MultiStatIncrease(
            {
                "strength": 35,
                "constitution": 55,
                "intelligence": -15,
                "wisdom": -10,
                "dexterity": -15,
                "agility": -15,
                "charisma": -10,
                "willpower": -5,
                "perception": -15,
                "luck": -5,
                }
        ),
                DerivedStatBonus("armor", 15),
                DerivedStatBonus("endurance", 25),
                DerivedStatBonus("cool", 10),
                ],
        tags=["giant"],
    ),

    "Gribbit": Race(
        name="Gribbit",
        effects_on_acquire=[MultiStatIncrease(
            {
                "constitution": 10,
                "intelligence": -10,
                "wisdom": 5,
                "dexterity": -10,
                "agility": 15,
                "charisma": -5,
                "willpower": -5,
                "perception": 5,
                "luck": -5,
                }
        ),
                DerivedStatBonus("armor", 5),
                DerivedStatBonus("mental_fortitude", 10),
                DerivedStatBonus("endurance", 5),
            ],
        tags=["amphibian"],
    ),

    "Halven": Race(
        name="Halven",
        effects_on_acquire=[MultiStatIncrease(
            {
                "strength": -10,
                "constitution": -10,
                "intelligence": -10,
                "wisdom": 10,
                "dexterity": 10,
                "agility": 10,
                "willpower": -10,
                "perception": -10,
                "luck": 10,
                }
        ),
                            ],
        tags=["humanoid"],
    ),

    "Human": Race(
        name="Human",
        tags=["humanoid"],
    ),

    "Raccant": Race(
        name="Raccant",
        effects_on_acquire=[MultiStatIncrease(
            {
                "strength": -15,
                "constitution": 15,
                "intelligence": -5,
                "wisdom": -10,
                "dexterity": 15,
                "agility": 15,
                "willpower": -15,
                "perception": -5,
                "luck": 5,
                }
        ),
                DerivedStatBonus("armor", 10),
                DerivedStatBonus("endurance", 5),
            ],
        tags=["beast"],
    ),

    "Toy Golem": Race(
        name="Toy Golem",
        requires_material=True,
        can_be_base=False,
        tags=["construct"],
    ),
}


# =========================================================
# RESOLUTION
# =========================================================

def get_all_races():
    return RACES.values()

def get_race(name: str) -> Race:
    if name not in RACES:
        raise ValueError(f"Race '{name}' not defined")
    return copy.deepcopy(RACES[name])


def resolve_race(name: str) -> Race:
    race = get_race(name)

    if not race.base_race:
        return race

    base = resolve_race(race.base_race)

    return Race(
        name=race.name,
        effects_on_acquire=(base.effects_on_acquire or []) + (race.effects_on_acquire or []),
        effects_per_level=(base.effects_per_level or []) + (race.effects_per_level or []),
        tags=list(set(base.tags + race.tags)),
        requires_material=race.requires_material,
        material=race.material,
        base_race=race.base_race,
    )
