import random
from src.domain.attributes import Attributes, Defenses, PoolManager, calculate_pools, DEFAULT_STATS
from src.domain.character import Character
from src.domain.race import resolve_race, apply_material_template

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

def roll_attributes(race) -> Attributes:
    """
    Generate Attributes object based on race + 2d10 rolls.
    """

    rolled_stats = {
        stat: DEFAULT_STATS[stat] + race.stat_modifiers.get(stat, 0) + roll_2d10()
        for stat in DEFAULT_STATS
    }

    return Attributes(
        **rolled_stats,
        race=race.name,
        adventure_job=None,
        adventure_level=0,
        craft_job=None,
        craft_level=0
    )

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

def create_character(name: str, race_name: str) -> Character:
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

    attrs = roll_attributes(race)
    pools = calculate_pools(attrs)
    defenses = calculate_defenses(attrs, race)

    # Assemble Character
    character = Character(
        name=name,
        attributes=attrs,
        pools=pools,
        defenses=defenses
    )

    return character


if __name__ == "__main__":
    my_char = create_character("Thorin", "Dwarf")
    print(f"Character: {my_char.name} ({my_char.attributes.race})")
    print(f"STR: {my_char.attributes.strength}, CON: {my_char.attributes.constitution}")
    print(f"HP: {my_char.pools.hp[0]}/{my_char.pools.hp[1]}")
