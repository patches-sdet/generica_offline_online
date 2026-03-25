import copy
from dataclasses import dataclass, field
from typing import List, Optional

from domain.effects import StatIncrease, Effect, DerivedStatBonus
from domain.attributes import Attributes, DEFAULT_STATS


# -------------------------
# CORE RACE MODEL
# -------------------------

@dataclass(frozen=True)
class Race:
    name: str
    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)

    requires_material: bool = False
    material: Optional[str] = None
    can_be_base: bool = True
    base_race: Optional[str] = None

    def get_display_name(self) -> str:
        if self.base_race and self.material:
            return (f"{self.name} ({self.material.title()} {self.base_race})")
        elif self.material:
            return (f"{self.name} ({self.material.titel()})")
        return self.name

    # -------------------------
    # BASE ATTRIBUTES
    # -------------------------

    def get_base_attributes(self, level: int) -> Attributes:
        """
        Base attributes are universal.
        Races modify via effects only.
        """
        return Attributes(**DEFAULT_STATS)

    # -------------------------

    def get_effects(self, level: int) -> List[Effect]:
        """
        Combine acquire + per-level effects.
        """
        effects = list(self.effects_on_acquire)

        for _ in range(level):
            effects.extend(self.effects_per_level)

        return effects

    # -------------------------

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "requires_material": self.requires_material,
            "material": self.material,
            "base_race": self.base_race,
        }


# -------------------------
# EFFECT HELPERS
# -------------------------

def make_effects(**mods):
    return [StatIncrease(stat, value) for stat, value in mods.items()]


# -------------------------
# RACE DEFINITIONS (ALPHABETICAL)
# -------------------------

RACES = {
    "Doll Haunter": Race(
        name="Doll Haunter",
        effects_on_acquire=[],
        requires_material=True,
        can_be_base = False
    ),

    "Dwarf": Race(
        name="Dwarf",
        effects_on_acquire=make_effects(
            strength=10,
            constitution=10,
            intelligence=-10,
            wisdom=10,
            agility=-10,
            charisma=-10,
            willpower=10,
            perception=-10,
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Elf": Race(
        name="Elf",
        effects_on_acquire=make_effects(
            strength=5,
            constitution=5,
            intelligence=5,
            wisdom=5,
            dexterity=5,
            agility=5,
            willpower=5,
            perception=5,
            luck=5,
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Frosted Giant": Race(
        name="Frosted Giant",
        effects_on_acquire=(
            make_effects(
                strength=35,
                constitution=55,
                intelligence=-15,
                wisdom=-10,
                dexterity=-15,
                agility=-15,
                charisma=-10,
                willpower=-5,
                perception=-15,
                luck=-5,
            )
            + [
                DerivedStatBonus("armor", 15),
                DerivedStatBonus("endurance", 25),
                DerivedStatBonus("cool", 10),
            ]
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Gribbit": Race(
        name="Gribbit",
        effects_on_acquire=(
            make_effects(
                constitution=10,
                intelligence=-10,
                wisdom=5,
                dexterity=-10,
                agility=15,
                charisma=-5,
                willpower=-5,
                perception=5,
                luck=-5,
            )
            + [
                DerivedStatBonus("armor", 5),
                DerivedStatBonus("mental_fortitude", 10),
                DerivedStatBonus("endurance", 5),
            ]
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Halven": Race(
        name="Halven",
        effects_on_acquire=make_effects(
            strength=-10,
            constitution=-10,
            intelligence=-10,
            wisdom=10,
            dexterity=10,
            agility=10,
            willpower=-10,
            perception=-10,
            luck=10,
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Human": Race(
        name="Human",
        effects_on_acquire=[],
        requires_material=False,
        can_be_base=True
    ),

    "Raccant": Race(
        name="Raccant",
        effects_on_acquire=(
            make_effects(
                strength=-15,
                constitution=15,
                intelligence=-5,
                wisdom=-10,
                dexterity=15,
                agility=15,
                willpower=-15,
                perception=-5,
                luck=5,
            )
            + [
                DerivedStatBonus("armor", 10),
                DerivedStatBonus("endurance", 5),
            ]
        ),
        requires_material=False,
        can_be_base=True
    ),

    "Toy Golem": Race(
        name="Toy Golem",
        base_race="Human",
        effects_on_acquire=[],
        requires_material=True,
        can_be_base=False
    ),
}


# -------------------------
# RACE RESOLUTION
# -------------------------

def get_race(name: str) -> Race:
    if name not in RACES:
        raise ValueError(f"Race '{name}' not defined")
    return copy.deepcopy(RACES[name])


def resolve_race(race: str) -> Race:
    """
    Resolve race including base race inheritance via effects.
    """
    race = get_race(race)

    if not race.base_race:
        return race

    base = resolve_race(race.base_race)

    return Race(
        name=race.name,
        effects_on_acquire=base.effects_on_acquire + race.effects_on_acquire,
        effects_per_level=base.effects_per_level + race.effects_per_level,
        requires_material=race.requires_material,
        material=race.material,
        base_race=base.name,
    )
