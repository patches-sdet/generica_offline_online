import random, copy
from domain.attributes import DEFAULT_STATS
from domain.character import Character
from domain.race import Race
from domain.adventure import AdventureJob
from domain.profession import ProfessionJob, get_all_professions
from domain.calculations import calculate_pools, recalculate
from domain.effects.stat_effects import StatIncrease, MultiStatIncrease
from domain.effects.special.damage import ConvertDamageEffect, BonusDamageEffect  # future-safe
from domain.effects.special.state import ApplyStateEffect
from domain.effects.special.tag import ApplyTagEffect
from domain.effects.base import Effect
from domain.progression import Progression

# ROLLING

def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_attributes() -> list[Effect]:
    effects = []

    for stat in DEFAULT_STATS:
        roll = roll_2d10()
        effects.append(StatIncrease(stat, roll))

    return effects

# MATERIAL SYSTEM

# DerivedStatOverride
from domain.effects import DerivedStatOverride


MATERIAL_EFFECTS = {
    "cloth": [
        DerivedStatOverride("armor", 10),
        DerivedStatOverride("endurance", 20),
    ],
    "leather": [
        DerivedStatOverride("armor", 15),
        DerivedStatOverride("endurance", 15),
    ],
    "metal": [
        DerivedStatOverride("armor", 20),
        DerivedStatOverride("endurance", 10),
    ],
}


def apply_material_to_race(race: Race, base_race: Race, material: str) -> Race:
    return Race(
        name=race.name,
        effects_on_acquire=race.effects_on_acquire + MATERIAL_EFFECTS[material],
        effects_per_level=base_race.effects_per_level + race.effects_per_level,
        requires_material=race.requires_material,
        material=material,
        base_race=base_race.name,
    )

# PROFESSION HELPERS

def list_professions():
    return get_all_professions()

# CORE CREATION

def create_character(
    name: str,
    race: Race,
    jobs: list[AdventureJob],
    professions: list[ProfessionJob],
    base_race: Race | None = None,
    material: str | None = None,
) -> Character:

    # MATERIAL HANDLING

    if race.requires_material:
        if base_race is None or material is None:
            raise ValueError(
                f"{race.name} requires base_race and material"
            )

        race = apply_material_to_race(copy.deepcopy(race), base_race, material)

    else:
        if base_race or material:
            raise ValueError(f"{race.name} does not support material")

    # VALIDATION

    if len(jobs) > race.max_adventure_jobs:
        raise ValueError(f"{race.name} allows only {race.max_adventure_jobs} jobs")

    if len(professions) > race.max_profession_jobs:
        raise ValueError(f"{race.name} allows only {race.max_profession_jobs} professions")

    # LEVEL STRUCTURES

    adventure_levels = {job.name: 1 for job in jobs}
    profession_levels = {prof.name: 1 for prof in professions}

    # ATTRIBUTE EFFECTS

    attribute_effects = roll_attributes()

    # CHARACTER INIT

    character = Character(
        name=name,
        race=race,
        race_levels={race.name: 1},
        base_race_levels={base_race.name: 1} if base_race else {},
        adventure_jobs=jobs,
        adventure_levels=adventure_levels,
        profession_jobs=professions,
        profession_levels=profession_levels,
    )

    for job in character.adventure_jobs:
        level = character.adventure_levels.get(job.name, 1)
        character.progressions[("adventure", job.name)] = Progression(
            name=job.name,
            type="adventure",
            level=level,
        )

    for job in character.profession_jobs:
        level = character.profession_levels.get(job.name, 1)
        character.progressions[("profession", job.name)] = Progression(
            name=job.name,
            type="profession",
            level=level,
        )

    character.progressions[("race", character.race.name)] = Progression(
        name=character.race.name,
        type="race",
        level=character.get_race_levels(),
    )

    # NEW: RUNTIME SYSTEM INIT

    character.states = {}
    character.tags = set()
    character.event_listeners = []

    character.next_attack_modifiers = []
    character.extra_attacks = 0
    character.bonus_damage = 0
    character.damage_conversion = None

    character.inventory = []

    # APPLY ATTRIBUTE EFFECTS

    character.attribute_effects = attribute_effects

    # FULL REBUILD

    recalculate(character)
    
    pools = calculate_pools(character)

    character.current_hp = pools.hp[1]
    character.current_sanity = pools.sanity[1]
    character.current_stamina = pools.stamina[1]
    character.current_moxie = pools.moxie[1]
    character.current_fortune = pools.fortune[1]

    return character
