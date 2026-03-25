import random, copy

from domain.attributes import Attributes, DEFAULT_STATS
from domain.character import Character
from domain.race import Race, resolve_race
from domain.adventure import AdventureJob
from domain.profession import ProfessionJob, get_all_professions
from domain.calculations import calculate_pools, recalculate
from domain.effects import DerivedStatOverride, Effect, StatIncrease

# =========================
# ROLLING
# =========================

def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_attributes() -> list[Effect]:
    effects = []

    for stat in DEFAULT_STATS:
        roll = roll_2d10()

        effects.append(
                StatIncrease(stat, roll)
                )

    return effects


# =========================
# MATERIAL SYSTEM
# =========================

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


# =========================
# PROFESSION SELECTION (LOGIC ONLY)
# =========================

def get_profession_by_name(name: str):
    return resolve_profession(name)


def list_professions():
    return get_all_professions()


# =========================
# CORE CREATION
# =========================

def create_character(
    name: str,
    race: Race,
    job: AdventureJob,
    profession: ProfessionJob,
    base_race: Race | None = None,
    material: str | None = None,
) -> Character:
    """
    Pure character creation (no input/print).
    """

    # Handle material-based races

    if race.requires_material:
        if base_race is None or material is None:
            raise ValueError(
                    f"{race} requires base_race and material, "
                    f"but got base_race={base_race}, material={material}"
                    )

        race = apply_material_to_race(copy.deepcopy(race), base_race, material)

    else:
        if base_race is not None or material is not None:
            raise ValueError(
                    f"{race} does not support base_race/material, "
                    f"but got base_race={base_race}, material={material}"
                    )

    roll_effects = roll_attributes()

    character = Character(
        name=name,
        race=race,
        race_level=1,
        base_race_level=1,
        adventure_job=job,
        adventure_level=1,
        profession_job=profession,
        profession_level=1,
    )

    character.attribute_effects = roll_effects
    
    # Build full state
    recalculate(character)

    # Initialize pools to max
    pools = calculate_pools(character)

    character.current_hp = pools.hp[1]
    character.current_sanity = pools.sanity[1]
    character.current_stamina = pools.stamina[1]
    character.current_moxie = pools.moxie[1]
    character.current_fortune = pools.fortune[1]

    return character
