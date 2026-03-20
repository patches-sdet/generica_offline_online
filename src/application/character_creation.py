import random
from domain.attributes import Attributes, Defenses, PoolManager, calculate_pools, DEFAULT_STATS
from domain.character import Character
from domain.race import resolve_race, apply_material_template
from domain.adventure import resolve_job
from domain.effects import StatIncrease
from domain.leveling import apply_effects

def roll_2d10() -> int:
    """
    Roll two 10-sided dice.
    """
    return random.randint(1, 10) + random.randint(1, 10)

ATTRIBUTE_NAMES = [
    "strength",
    "constitution",
    "intelligence",
    "wisdom",
    "dexterity",
    "agility",
    "charisma",
    "willpower",
    "perception",
    "luck"
]

def roll_attributes() -> Attributes:
    """
    Generate Attributes object based on race + 2d10 rolls.
    """

    rolled_stats = {
        stat: DEFAULT_STATS[stat] + roll_2d10()
        for stat in DEFAULT_STATS
    }

    return Attributes(**rolled_stats)

def calculate_defenses(attrs: Attributes, race) -> Defenses:
    """
    Calculate defenses based on attribute values.
    """
    return Defenses(
        armor=race.racial_armor,
        mental_fortitude=race.racial_mental_fortitude,
        endurance=race.racial_endurance,
        cool=race.racial_cool,
        fate=race.racial_fate
    )

def create_character(name: str, race_name: str, job_name: str) -> Character:
    """
    Generate a full Character object with attributes, pools, and defenses.
    """
    
    race = resolve_race(race_name)
    
    if race.requires_material:
        print("\nChoose material:")
        print("- cloth\n- leather\n- metal")

        material = input("Material: ").strip().lower()
        while material not in ["cloth", "leather", "metal"]:
            material = input("Invalid. Choose cloth, leather, or metal: ").strip().lower()
            
        race = apply_material_template(race, material)

    job = resolve_job(job_name)
    attrs = roll_attributes()
    pools = calculate_pools(character)
    defenses = calculate_defenses(attrs, race)

    character.current_hp = pools.hp[1]
    character.current_sanity = pools.sanity[1]
    character.current_stamina = pools.stamina[1]
    character.current_moxie = pools.moxie[1]
    character.current_fortune = pools.fortune[1]

    # Assemble Character
    character = Character(
        name=name,
        race=race,
        race_level=0,
        adventure_job=job,
        adventure_level=0,
        profession_job=None,
        profession_level=0,
        attributes=attrs,
        pools=pools,
        defenses=defenses
    )

    apply_effects(race.effects_on_acquire, character)
    apply_effects(job.effects_on_acquire, character)

    return character
