import random

from domain.attributes import DEFAULT_STATS
from domain.character import Character
from domain.progression import Progression

from domain.calculations import calculate_pools, recalculate
from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease

from domain.content_registry import (
    get_base_race,
    get_race_template,
    get_adventure_job,
    get_profession_job,
)
from domain.race_resolution import MATERIAL_EFFECTS, get_race_display_name

# Rolling

def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_attributes() -> list[Effect]:
    effects: list[Effect] = []

    for stat in DEFAULT_STATS:
        effects.append(StatIncrease(stat, roll_2d10(), source="roll"))

    return effects

# Internal helpers

def _initialize_runtime_state(character: Character) -> None:
    if not hasattr(character, "states") or character.states is None:
        character.states = {}

    if not hasattr(character, "tags") or character.tags is None:
        character.tags = set()

    if not hasattr(character, "event_listeners") or character.event_listeners is None:
        character.event_listeners = []

    if not hasattr(character, "next_attack_modifiers") or character.next_attack_modifiers is None:
        character.next_attack_modifiers = []

    if not hasattr(character, "extra_attacks"):
        character.extra_attacks = 0

    if not hasattr(character, "bonus_damage"):
        character.bonus_damage = 0

    if not hasattr(character, "damage_conversion"):
        character.damage_conversion = None

    if not hasattr(character, "roll_modifiers") or character.roll_modifiers is None:
        character.roll_modifiers = []

    if not hasattr(character, "inventory") or character.inventory is None:
        character.inventory = []

    if not hasattr(character, "equipment") or character.equipment is None:
        character.equipment = []

    if not hasattr(character, "active_effects") or character.active_effects is None:
        character.active_effects = []


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
        character.progressions[("race", base_name)] = Progression(
            name=base_name,
            type="race",
            level=1,
        )

    template = get_race_template(character.race_template) if character.race_template else None
    if template and template.kind == "overlay":
        character.add_progression("race", template.name, 1)

    for name in adventure_job_names:
        character.progressions[("adventure", name)] = Progression(
            name=name,
            type="adventure",
            level=1,
        )

    for name in profession_job_names:
        character.progressions[("profession", name)] = Progression(
            name=name,
            type="profession",
            level=1,
        )

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

    base_races = [get_base_race(name) for name in base_race_names]
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

    attribute_effects = roll_attributes()

    # Compatibility fields retained only where useful
    primary_base = base_races[0]

    character = Character(
    name=name,
    race_bases=[base.name for base in base_races],
    race_template=race_template.name if race_template else None,
    race_material=material,
)

    character.attribute_effects = attribute_effects

    _initialize_runtime_state(character)

    # Also mirror into states for compatibility
    if character.race_template:
        character.states["race_template"] = character.race_template
    if character.race_material:
        character.states["race_material"] = character.race_material

    _register_progressions(
        character,
        race_bases=character.race_bases,
        adventure_job_names=[job.name for job in jobs],
        profession_job_names=[prof.name for prof in professions],
    )

    recalculate(character)
    _initialize_current_resources_to_max(character)

    return character