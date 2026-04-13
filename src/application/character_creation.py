import random
from domain.attributes import DEFAULT_STATS
from domain.character import Character
from domain.progression import Progression
from domain.skill_ownership import set_skill_levels
from domain.calculations import calculate_pools, recalculate
from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease

from domain.content_registry import (
    get_base_race,
    get_race_template,
    get_adventure_job,
    get_profession_job,
)
from domain.race_resolution import get_race_effects
from domain.skill_ownership import set_skill_levels

# Rolling

def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_attributes() -> list[Effect]:
    effects: list[Effect] = []

    for stat in DEFAULT_STATS:
        effects.append(StatIncrease(stat, roll_2d10(), source="roll"))

    return effects

def _initialize_current_resources_to_max(character: Character) -> None:
    pools = calculate_pools(character)

    character.current_hp = pools.hp[1]
    character.current_sanity = pools.sanity[1]
    character.current_stamina = pools.stamina[1]
    character.current_moxie = pools.moxie[1]
    character.current_fortune = pools.fortune[1]

def _register_progressions(
    character: Character,
    *,
    race_bases: list[str],
    adventure_job_names: list[str],
    profession_job_names: list[str],
) -> None:
    for base_name in race_bases:
        character.add_progression("race", base_name, 1), Progression(
            name=base_name,
            type="race",
            level=1,
        )

    template = get_race_template(character.race_template) if character.race_template else None
    if template and template.kind == "overlay":
        character.add_progression("race", template.name, 1)

    for name in adventure_job_names:
        character.add_progression("adventure", name, 1), Progression(
            name=name,
            type="adventure",
            level=1,
        )

    for name in profession_job_names:
        character.add_progression("profession", name, 1), Progression(
            name=name,
            type="profession",
            level=1,
        )

def _build_creation_base_attributes(
    character: Character,
    roll_effects: list[Effect],
) -> dict[str, int]:
    """
    Creation-time immutable base:
      DEFAULT_STATS
      + rolled attribute variance
      + racial/template/material acquire effects at level 1
    """
    base = dict(DEFAULT_STATS)

    # Apply the 2d10 roll layer
    for effect in roll_effects:
        if isinstance(effect, StatIncrease):
            base[effect.stat] += effect.amount

    # Apply racial/template/material level-1 effects.
    for effect in get_race_effects(character):
        if isinstance(effect, StatIncrease):
            base[effect.stat] += effect.amount

    return base

def _seed_character_base_state(
    character: Character,
    roll_effects: list[Effect],
) -> None:
    """
    Persist the creation-time base so recalculate() can rebuild from it later.
    """
    character._base_attributes = _build_creation_base_attributes(character, roll_effects)

    # NOTE FOR LATER DEV:
    # character.attribute_effects used to hold roll effects for older rebuild logic.
    # With progressions + _base_attributes now canonical, this field should be
    # considered transitional / removable once the rest of the pipeline no longer
    # references it anywhere.
    character.attribute_effects = []

def apply_generic_skill_allocation(character, allocations: dict[str, int]) -> None:
        """
        allocations example:
        {
            "Riding": 10,
            "Sword": 15,
            "Awareness": 5,
        }
        """
        for skill_name, levels in allocations.items():
            if levels < 0:
                raise ValueError(f"Generic skill levels cannot be negative: {skill_name}={levels}")
            set_skill_levels(character, skill_name, source="generic_points", levels=levels)


def apply_job_skill_allocation(character, allocations: dict[str, dict[str, int]]) -> None:
    """
    allocations example:
    {
        "Berserker": {"Growl": 10, "Toughness": 5},
        "Cleric": {"Faith": 10, "Lesser Healing": 5},
    }
    """
    for job_name, skill_map in allocations.items():
        for skill_name, level in skill_map.items():
            if level < 0:
                raise ValueError(f"Job skill levels cannot be negative: {job_name}.{skill_name}={level}")
            set_skill_levels(character, skill_name, source=f"job_points:{job_name}", levels=level)

# Public API

def create_character(
    *,
    name: str,
    base_race_names: list[str],
    adventure_job_names: list[str],
    profession_job_names: list[str],
    race_template_name: str | None = None,
    material: str | None = None,
) -> Character:
    if not base_race_names:
        raise ValueError("Character must have at least one base race")

    base_races = [get_base_race(race_name) for race_name in base_race_names]
    jobs = [get_adventure_job(job_name) for job_name in adventure_job_names]
    professions = [get_profession_job(job_name) for job_name in profession_job_names]

    race_template = get_race_template(race_template_name) if race_template_name else None

    if race_template and race_template.kind == "composition":
        if race_template.name == "Crossbreed":
            if len(base_races) != 2:
                raise ValueError("Crossbreed requires exactly two base races")
        else:
            raise ValueError(f"Unsupported composition template: {race_template.name}")
    else:
        if len(base_races) != 1:
            raise ValueError("Non-composition races require exactly one base race")

    if race_template and race_template.requires_material and material is None:
        raise ValueError(f"{race_template.name} requires material")

    if race_template and not race_template.requires_material and material is not None:
        raise ValueError(f"{race_template.name} does not use material")

    # Job limits: use the most restrictive base race limit for multi-base cases
    max_adventure_jobs = min(base.max_adventure_jobs for base in base_races)
    max_profession_jobs = min(base.max_profession_jobs for base in base_races)

    if len(jobs) > max_adventure_jobs:
        raise ValueError(f"Race allows only {max_adventure_jobs} adventure job(s)")

    if len(professions) > max_profession_jobs:
        raise ValueError(f"Race allows only {max_profession_jobs} profession job(s)")

    roll_effects = roll_attributes()

    character = Character(
        name=name,
        race_bases=[base.name for base in base_races],
        race_template=race_template.name if race_template else None,
        race_material=material,
    )

    _register_progressions(
        character,
        race_bases=character.race_bases,
        adventure_job_names=[job.name for job in jobs],
        profession_job_names=[profession.name for profession in professions],
    )

    _seed_character_base_state(character, roll_effects)

    recalculate(character)
    _initialize_current_resources_to_max(character)

    return character
