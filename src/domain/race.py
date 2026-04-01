from dataclasses import dataclass, field
from math import ceil, floor
from typing import Literal, Optional
from domain.content_registry import get_base_race, get_race_template
from domain.effects.base import Effect
from domain.effects.stat_effects import MultiStatIncrease, DerivedStatBonus

TemplateKind = Literal["overlay", "composition"]

# MODELS

@dataclass(frozen=True, slots=True)
class BaseRace:
    name: str
    acquire_stats: dict[str, int] = field(default_factory=dict)
    level_stats: dict[str, int] = field(default_factory=dict)
    acquire_derived: dict[str, int] = field(default_factory=dict)
    level_derived: dict[str, int] = field(default_factory=dict)
    tags: tuple[str, ...] = field(default_factory=tuple)
    max_adventure_jobs: int = 1
    max_profession_jobs: int = 1

    # Crossbreed support
    starting_racial_skills: tuple[str, ...] = field(default_factory=tuple)
    crossbreed_eligible: bool = False

    def effects_on_acquire(self) -> list[Effect]:
        effects: list[Effect] = []
        if self.acquire_stats:
            effects.append(MultiStatIncrease(dict(self.acquire_stats)))

        for stat, value in self.acquire_derived.items():
            effects.append(DerivedStatBonus(stat, value))
        return effects

    def get_effects(self, level: int = 1) -> list[Effect]: # Level-up Effects
        level = max(1, level)
        if level <= 1:
            return []

        per_level: list[Effect] = []
        if self.level_stats:
            per_level.append(MultiStatIncrease(dict(self.level_stats)))

        for stat, value in self.level_derived.items():
            per_level.append(DerivedStatBonus(stat, value))
        return per_level * (level - 1)


@dataclass(frozen=True, slots=True)
class RaceTemplate:
    name: str
    kind: TemplateKind = "overlay"
    acquire_stats: dict[str, int] = field(default_factory=dict)
    level_stats: dict[str, int] = field(default_factory=dict)
    acquire_derived: dict[str, int] = field(default_factory=dict)
    level_derived: dict[str, int] = field(default_factory=dict)
    tags: tuple[str, ...] = field(default_factory=tuple)
    requires_material: bool = False

    def effects_on_acquire(self) -> list[Effect]:
        effects: list[Effect] = []
        if self.acquire_stats:
            effects.append(MultiStatIncrease(dict(self.acquire_stats)))

        for stat, value in self.acquire_derived.items():
            effects.append(DerivedStatBonus(stat, value))
        return effects

    def get_effects(self, level: int = 1) -> list[Effect]: # Template Level-Up Effects
        level = max(1, level)
        if level <= 1:
            return []

        per_level: list[Effect] = []

        if self.level_stats:
            per_level.append(MultiStatIncrease(dict(self.level_stats)))

        for stat, value in self.level_derived.items():
            per_level.append(DerivedStatBonus(stat, value))

        return per_level * (level - 1)

# HELPERS

def _merge_tags(*tag_groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    for group in tag_groups:
        for tag in group:
            if tag not in ordered:
                ordered.append(tag)
    return tuple(ordered)


def _average_dicts(
    left: dict[str, int],
    right: dict[str, int],
    round_mode: Literal["down", "up"],
) -> dict[str, int]:
    keys = set(left) | set(right)
    result: dict[str, int] = {}

    for key in keys:
        avg = (left.get(key, 0) + right.get(key, 0)) / 2
        result[key] = floor(avg) if round_mode == "down" else ceil(avg)
    return result


def _validate_crossbreed_parent(parent: BaseRace) -> None:
    if not parent.crossbreed_eligible:
        raise ValueError(f"{parent.name} is not eligible for Crossbreed")

    if len(parent.starting_racial_skills) != 2:
        raise ValueError(
            f"{parent.name} must define exactly two starting racial skills "
            f"to be Crossbreed-eligible"
        )

# RACE MECHANICS

def build_crossbreed_race(
    parent_a: BaseRace,
    parent_b: BaseRace,
) -> BaseRace:
    _validate_crossbreed_parent(parent_a)
    _validate_crossbreed_parent(parent_b)

    return BaseRace(
        name=f"Crossbreed ({parent_a.name}/{parent_b.name})",
        acquire_stats=_average_dicts(parent_a.acquire_stats, parent_b.acquire_stats, "down"),
        level_stats=_average_dicts(parent_a.level_stats, parent_b.level_stats, "up"),
        acquire_derived=_average_dicts(parent_a.acquire_derived, parent_b.acquire_derived, "down"),
        level_derived=_average_dicts(parent_a.level_derived, parent_b.level_derived, "up"),
        tags=_merge_tags(parent_a.tags, parent_b.tags, ("crossbreed",)),
        max_adventure_jobs=(parent_a.max_adventure_jobs + parent_b.max_adventure_jobs) // 2,
        max_profession_jobs=(parent_a.max_profession_jobs + parent_b.max_profession_jobs) // 2,
        starting_racial_skills=(
            parent_a.starting_racial_skills[0],
            parent_b.starting_racial_skills[0],
        ),
        crossbreed_eligible=False,
    )


def get_race_effects(character) -> list[Effect]:
    effects: list[Effect] = []
    base_names: list[str] = list(getattr(character, "race_bases", []))
    template_name: Optional[str] = getattr(character, "race_template", None)
    template = get_race_template(template_name) if template_name else None

    if not base_names:
        return effects

    # Composition template: Crossbreed
    if template and template.kind == "composition":
        if template.name != "Crossbreed":
            raise ValueError(f"Unsupported composition template: {template.name}")

        if len(base_names) != 2:
            raise ValueError("Crossbreed requires exactly two parent races")

        parent_a = get_base_race(base_names[0])
        parent_b = get_base_race(base_names[1])
        composite = build_crossbreed_race(parent_a, parent_b)

        level_a = character.get_progression_level("race", base_names[0], 0)
        level_b = character.get_progression_level("race", base_names[1], 0)
        level = max(1, min(level_a, level_b))

        effects.extend(composite.effects_on_acquire())
        effects.extend(composite.get_effects(level))
        return effects

    # Normal base race handling
    highest_base_level = 1

    for base_name in base_names:
        base = get_base_race(base_name)
        level = max(1, character.get_progression_level("race", base_name, 0))
        highest_base_level = max(highest_base_level, level)

        effects.extend(base.effects_on_acquire())
        effects.extend(base.get_effects(level))

    # Overlay template handling
    if template and template.kind == "overlay":
        effects.extend(template.effects_on_acquire())
        effects.extend(template.get_effects(highest_base_level))

    return effects


def get_race_tags(character) -> tuple[str, ...]:
    base_names: list[str] = list(getattr(character, "race_bases", []))
    template_name: Optional[str] = getattr(character, "race_template", None)
    template = get_race_template(template_name) if template_name else None

    if template and template.kind == "composition":
        if template.name != "Crossbreed":
            raise ValueError(f"Unsupported composition template: {template.name}")
        if len(base_names) != 2:
            raise ValueError("Crossbreed requires exactly two parent races")

        parent_a = get_base_race(base_names[0])
        parent_b = get_base_race(base_names[1])
        composite = build_crossbreed_race(parent_a, parent_b)
        return composite.tags

    tags: tuple[str, ...] = tuple()

    for base_name in base_names:
        tags = _merge_tags(tags, get_base_race(base_name).tags)

    if template:
        tags = _merge_tags(tags, template.tags)

    return tags

# Race Definitions

BASE_RACE_DEFINITIONS: tuple[BaseRace, ...] = (
    BaseRace(
        name="Human",
        acquire_stats={},
        level_stats={
            "strength": 3,
            "constitution": 3,
            "intelligence": 3,
            "wisdom": 3,
            "dexterity": 3,
            "agility": 3,
            "charisma": 3,
            "willpower": 3,
            "perception": 3,
            "luck": 3,
        },
        acquire_derived={},
        level_derived={
            "armor": 1,
            "mental_fortitude": 3,
            "endurance": 3,
            "cool": 3,
        },
        tags=("humanoid",),
        max_adventure_jobs=7,
        max_profession_jobs=3,
        starting_racial_skills=("Adaptable", "Generalist"),
        crossbreed_eligible=True,
    ),
    BaseRace(
        name="Elf",
        acquire_stats={
            "strength": 5,
            "constitution": 5,
            "intelligence": 5,
            "wisdom": 5,
            "dexterity": 5,
            "agility": 5,
            "willpower": 5,
            "perception": 5,
            "luck": 5,
        },
        level_stats={
            "strength": 3,
            "constitution": 3,
            "intelligence": 3,
            "wisdom": 3,
            "dexterity": 3,
            "agility": 3,
            "charisma": 3,
            "willpower": 3,
            "perception": 3,
            "luck": 3,
        },
        acquire_derived={},
        level_derived={
            "cool": 2,
            "endurance": 2,
            "mental_fortitude": 2,
        },
        tags=("humanoid",),
        max_adventure_jobs=6,
        max_profession_jobs=3,
        starting_racial_skills=("Grace", "Keen Senses"),
        crossbreed_eligible=True,
    ),
    BaseRace(
        name="Dwarf",
        acquire_stats={
            "strength": 10,
            "constitution": 10,
            "intelligence": -10,
            "wisdom": 10,
            "agility": -10,
            "charisma": -10,
            "willpower": 10,
            "perception": -10,
        },
        level_stats={
            "strength": 4,
            "constitution": 4,
            "wisdom": 4,
            "willpower": 4,
        },
        acquire_derived={},
        level_derived={},
        tags=("humanoid",),
        max_adventure_jobs=5,
        max_profession_jobs=5,
        starting_racial_skills=("Stoneblood", "Craft Affinity"),
        crossbreed_eligible=True,
    ),
    BaseRace(
        name="Halven",
        acquire_stats={
            "strength": -10,
            "constitution": -10,
            "intelligence": -10,
            "wisdom": 10,
            "dexterity": 10,
            "agility": 10,
            "willpower": -10,
            "perception": -10,
            "luck": 10,
        },
        level_stats={
            "strength": 2,
            "constitution": 2,
            "intelligence": 2,
            "wisdom": 2,
            "dexterity": 4,
            "agility": 4,
            "charisma": 4,
            "willpower": 4,
            "perception": 2,
            "luck": 4,
        },
        acquire_derived={},
        level_derived={
            "mental_fortitude": 3,
            "cool": 3,
        },
        tags=("humanoid",),
        max_adventure_jobs=6,
        max_profession_jobs=3,
        starting_racial_skills=("Lucky", "Quiet Step"),
        crossbreed_eligible=True,
    ),
    BaseRace(
        name="Orc",
        acquire_stats={
            "strength": 15,
            "constitution": 15,
            "intelligence": -15,
            "wisdom": -15,
            "dexterity": 15,
            "agility": 15,
            "charisma": -15,
            "willpower": -15,
            "perception": -10,
            "luck": -10,
        },
        level_stats={
            "strength": 5,
            "constitution": 5,
            "intelligence": 1,
            "wisdom": 1,
            "dexterity": 5,
            "agility": 5,
            "charisma": 1,
            "willpower": 1,
            "perception": 1,
            "luck": 1,
        },
        acquire_derived={},
        level_derived={
            "armor": 5,
            "endurance": 5,
        },
        tags=("humanoid",),
        max_adventure_jobs=6,
        max_profession_jobs=2,
        starting_racial_skills=("Savage Vigor", "Battle Instinct"),
        crossbreed_eligible=True,
    ),
    BaseRace(
        name="Gribbit",
        acquire_stats={
            "constitution": 10,
            "intelligence": -10,
            "wisdom": 5,
            "dexterity": -10,
            "agility": 15,
            "charisma": -5,
            "willpower": -5,
            "perception": 5,
            "luck": -5,
        },
        level_stats={
            "constitution": 4,
            "agility": 4,
            "perception": 4,
            "strength": 3,
            "wisdom": 3,
            "willpower": 2,
            "intelligence": 2,
            "charisma": 2,
            "dexterity": 2,
            "luck": 2,
        },
        acquire_derived={
            "armor": 5,
            "mental_fortitude": 10,
            "endurance": 5,
        },
        level_derived={
            "armor": 2,
            "endurance": 2,
            "mental_fortitude": 5,
        },
        tags=("amphibian", "humanoid"),
        max_adventure_jobs=1,
        max_profession_jobs=1,
        starting_racial_skills=(),
        crossbreed_eligible=False,
    ),
    BaseRace(
        name="Raccant",
        acquire_stats={
            "strength": -15,
            "constitution": 15,
            "intelligence": -5,
            "wisdom": -10,
            "dexterity": 15,
            "agility": 15,
            "willpower": -15,
            "perception": -5,
            "luck": 5,
        },
        level_stats={
            "strength": 1,
            "constitution": 4,
            "intelligence": 3,
            "wisdom": 2,
            "dexterity": 4,
            "agility": 4,
            "charisma": 3,
            "willpower": 1,
            "perception": 3,
            "luck": 3,
        },
        acquire_derived={
            "armor": 10,
            "endurance": 5,
        },
        level_derived={
            "armor": 3,
            "endurance": 3,
            "mental_fortitude": 2,
            "cool": 2,
        },
        tags=("monster", "humanoid"),
        max_adventure_jobs=4,
        max_profession_jobs=2,
        starting_racial_skills=(),
        crossbreed_eligible=False,
    ),
    BaseRace(
        name="Frosted Giant",
        acquire_stats={
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
        },
        level_stats={
            "strength": 11,
            "constitution": 11,
            "intelligence": 1,
            "wisdom": 1,
            "dexterity": 1,
            "agility": 1,
            "charisma": 1,
            "willpower": 1,
            "perception": 1,
            "luck": 1,
        },
        acquire_derived={
            "armor": 15,
            "endurance": 25,
            "cool": 10,
        },
        level_derived={
            "armor": 5,
            "endurance": 5,
        },
        tags=("giant",),
        max_adventure_jobs=4,
        max_profession_jobs=2,
        starting_racial_skills=(),
        crossbreed_eligible=False,
    ),
)

RACE_TEMPLATE_DEFINITIONS: tuple[RaceTemplate, ...] = (
    RaceTemplate(
        name="Doll Haunter",
        kind="overlay",
        acquire_stats={},
        level_stats={
            "strength": 2,
            "constitution": 2,
            "intelligence": 2,
            "wisdom": 2,
            "dexterity": 2,
            "agility": 2,
            "willpower": 2,
            "perception": 2,
            "charisma": 2,
            "luck": 2,
        },
        acquire_derived={},
        level_derived={},
        tags=("construct",),
        requires_material=True,
    ),
    RaceTemplate(
        name="Toy Golem",
        kind="overlay",
        acquire_stats={},
        level_stats={
            "strength": 2,
            "constitution": 2,
            "intelligence": 2,
            "wisdom": 2,
            "dexterity": 2,
            "agility": 2,
            "charisma": 2,
            "willpower": 2,
            "perception": 2,
            "luck": 2,
        },
        acquire_derived={},
        level_derived={},
        tags=("construct",),
        requires_material=True,
    ),
    RaceTemplate(
        name="Crossbreed",
        kind="composition",
        acquire_stats={},
        level_stats={},
        acquire_derived={},
        level_derived={},
        tags=("crossbreed",),
        requires_material=False,
    ),
)