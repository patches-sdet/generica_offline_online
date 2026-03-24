import random, copy

from domain.attributes import Attributes, DEFAULT_STATS
from domain.character import Character
from domain.race import resolve_race, Race
from domain.adventure import resolve_job
from domain.profession import resolve_profession, get_all_professions
from domain.calculations import calculate_pools, recalculate
from domain.effects import DerivedStatOverride

# =========================
# ROLLING
# =========================

def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_attributes() -> Attributes:
    rolled = {
        stat: DEFAULT_STATS[stat] + roll_2d10()
        for stat in DEFAULT_STATS
    }
    return Attributes(**rolled)


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
    race_name: str,
    job_name: str,
    profession_name: str,
    base_race_name: str | None = None,
    material: str | None = None,
) -> Character:
    """
    Pure character creation (no input/print).
    """

    race = resolve_race(race_name)

    # Handle material-based races
    if race.requires_material:
        if not base_race_name or not material:
            raise ValueError("Material races require base_race_name and material")

        base_race = resolve_race(base_race_name)
        race = apply_material_to_race(copy.deepcopy(race), base_race, material)

    job = resolve_job(job_name)
    profession = resolve_profession(profession_name)

    attrs = roll_attributes()

    character = Character(
        name=name,
        race=race,
        race_level=1,
        base_race_level=1,
        adventure_job=job,
        adventure_level=1,
        profession_job=profession,
        profession_level=1,
        attributes=attrs,
    )

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
