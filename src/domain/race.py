from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Literal
from domain.effects.base import Effect
from domain.effects.stat_effects import MultiStatIncrease, DerivedStatBonus


# =========================================================
# MODELS
# =========================================================

@dataclass(frozen=True, slots=True)
class BaseRace:
    name: str

    effects_on_acquire: Tuple[Effect, ...] = field(default_factory=tuple)
    effects_per_level: Tuple[Effect, ...] = field(default_factory=tuple)

    tags: Tuple[str, ...] = field(default_factory=tuple)

    max_adventure_jobs: int = 1
    max_profession_jobs: int = 1

    starting_racial_skills: Tuple[str, ...] = field(default_factory=tuple)
    crossbreed_eligible: bool = False


@dataclass(frozen=True, slots=True)
class RaceTemplate:
    name: str
    kind: Literal["overlay", "composition"] = "overlay"

    effects_on_acquire: Tuple[Effect, ...] = field(default_factory=tuple)
    effects_per_level: Tuple[Effect, ...] = field(default_factory=tuple)
    tags: Tuple[str, ...] = field(default_factory=tuple)

    requires_material: bool = False

# REGISTRIES

BASE_RACE_REGISTRY: dict[str, BaseRace] = {}
RACE_TEMPLATE_REGISTRY: dict[str, RaceTemplate] = {}


def register_base_race(race: BaseRace):
    BASE_RACE_REGISTRY[race.name] = race


def register_template(template: RaceTemplate):
    RACE_TEMPLATE_REGISTRY[template.name] = template


def get_base_race(name: str) -> BaseRace:
    return BASE_RACE_REGISTRY[name]


def get_template(name: Optional[str]) -> Optional[RaceTemplate]:
    if not name:
        return None
    return RACE_TEMPLATE_REGISTRY[name]

# EFFECT RESOLUTION

def get_race_effects(character) -> List[Effect]:
    """
    Unified race effect resolution.

    Supports:
    - Base races
    - Templates (Doll Haunter, Toy Golem)
    - Multi-base (Half-Breed)
    """

    effects: List[Effect] = []

    base_names: List[str] = getattr(character, "race_bases", [])
    template_name: Optional[str] = getattr(character, "race_template", None)

    template = get_template(template_name)

    # BASE RACES

    for base_name in base_names:
        base = get_base_race(base_name)
        level = character.get_progression_level(base_name, "race")

        if level >= 1:
            effects.extend(base.effects_on_acquire)

        if level > 1:
            effects.extend(base.effects_per_level * (level - 1))

    # TEMPLATE EFFECTS

    if template:
        # Half-Breed special rule:
        # Split level across bases or apply once (design choice)
        if template.name == "Half-Breed":
            # Simple version: apply template once at max level
            max_level = max(
                (character.get_progression_level(b, "race") for b in base_names),
                default=1
            )

            if max_level >= 1:
                effects.extend(template.effects_on_acquire)

            if max_level > 1:
                effects.extend(template.effects_per_level * (max_level - 1))

        else:
            # Normal templates scale with first base
            if base_names:
                level = character.get_progression_level(base_names[0], "race")

                if level >= 1:
                    effects.extend(template.effects_on_acquire)

                if level > 1:
                    effects.extend(template.effects_per_level * (level - 1))

    return effects

# BASE RACE DEFINITIONS

register_base_race(BaseRace(
    name="Human",
    effects_per_level=(
        MultiStatIncrease({
            "strength": 3, "constitution": 3, "intelligence": 3,
            "wisdom": 3, "dexterity": 3, "agility": 3,
            "charisma": 3, "willpower": 3, "perception": 3, "luck": 3,
        }),
        DerivedStatBonus("armor", 1),
        DerivedStatBonus("mental_fortitude", 3),
        DerivedStatBonus("endurance", 3),
        DerivedStatBonus("cool", 3),
    ),
    max_adventure_jobs=7,
    max_profession_jobs=3,
    tags=("humanoid",),
))


register_base_race(BaseRace(
    name="Elf",
    effects_on_acquire=(
        MultiStatIncrease({
            "strength": 5, "constitution": 5, "intelligence": 5,
            "wisdom": 5, "dexterity": 5, "agility": 5,
            "willpower": 5, "perception": 5, "luck": 5,
        }),
    ),
    effects_per_level=(
        MultiStatIncrease({
            "strength": 3, "constitution": 3, "intelligence": 3,
            "wisdom": 3, "dexterity": 3, "agility": 3,
            "charisma": 3, "willpower": 3, "perception": 3, "luck": 3,
        }),
        DerivedStatBonus("cool", 2),
        DerivedStatBonus("endurance", 2),
        DerivedStatBonus("mental_fortitude", 2),
    ),
    max_adventure_jobs=6,
    max_profession_jobs=3,
    tags=("humanoid",),
))


# (Add the rest of your base races exactly the same way)

# Templates

register_template(RaceTemplate(
    name="Doll Haunter",
    kind="overlay",
    requires_material=True,
    effects_per_level=(
        MultiStatIncrease({
            "strength": 2, "constitution": 2, "intelligence": 2,
            "wisdom": 2, "dexterity": 2, "agility": 2,
            "willpower": 2, "perception": 2, "charisma": 2, "luck": 2,
        }),
    ),
    tags=("construct",),
))


register_template(RaceTemplate(
    name="Toy Golem",
    kind="overlay",
    requires_material=True,
    effects_per_level=(
        MultiStatIncrease({
            "strength": 2, "constitution": 2, "intelligence": 2,
            "wisdom": 2, "dexterity": 2, "agility": 2,
            "charisma": 2, "willpower": 2, "perception": 2, "luck": 2,
        }),
    ),
    tags=("construct",),
))


register_template(RaceTemplate(
    name="Half-Breed",
    kind="composition",
    requires_material=False,
    effects_on_acquire=(
        DerivedStatBonus("cool", 2),
        DerivedStatBonus("mental_fortitude", 2),
    ),
    effects_per_level=(
        MultiStatIncrease({
            "strength": 2, "constitution": 2, "dexterity": 2,
            "agility": 2, "charisma": 2,
        }),
    ),
    tags=("hybrid",),
))