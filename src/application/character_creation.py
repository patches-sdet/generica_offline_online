import random
from domain.attributes import Attributes, DEFAULT_STATS
from domain.character import Character
from domain.race import Race, resolve_race
from domain.adventure import resolve_job
from domain.calculations import calculate_pools, recalculate
from domain.effects import DerivedStatOverride
from domain.craft import get_all_professions, resolve_profession

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

def roll_attributes() -> Attributes:
    """
    Generate Attributes object based on DEFAULT_STATS + 2d10 rolls.
    """

    rolled_stats = {
        stat: DEFAULT_STATS[stat] + roll_2d10()
        for stat in DEFAULT_STATS
    }

    return Attributes(**rolled_stats)

def create_character(name: str, race_name: str, job_name: str) -> Character:
    """
    Generate a full Character object with attributes, pools, and defenses.
    """
    
    race = resolve_race(race_name)
    
    if race.requires_material:
        print("Choose a base race:")

        from domain.race import RACES

        base_race_names = [
                r.name for r in RACES.values()
                if not r.requires_material
                ]
        for r in base_race_names:
            print(f"- {r}")
        
        base_choice = input("Base Race: ").strip()

        while base_choice not in base_race_names:
            base_choice = input("Invalid choice, choose a valid base race: ").strip()

        base_race = resolve_race(base_choice)

        print("\nChoose material:")
        print("- Cloth\n- Leather\n- Metal")

        material = input("Material: ").strip().lower()
        while material not in ["cloth", "leather", "metal"]:
            material = input("Invalid. Choose Cloth, Leather, or Metal: ").strip().lower()

        race = Race(
                name = race.name,
                effects_on_acquire = race.effects_on_acquire + MATERIAL_EFFECTS[material],
                effects_per_level = base_race.effects_per_level + race.effects_per_level,
                requires_material = race.requires_material,
                )
    def choose_profession():
        professions = get_all_professions()

        while True:
            print("Choose a profession:")
            for i, prof in enumerate(professions, 1):
                print(f"{i}. {prof.name}")

            choice = input("> ").strip()

            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(professions):
                    return professions[index]
                else:
                    try:
                        return resolve_professions(choice)
                    except ValueError:
                        pass
                print("Invalid choice. Try again")

        return professions[choice]

    job = resolve_job(job_name)
    chosen_professions = choose_profession()
    attrs = roll_attributes()

    # Assemble Character
    character = Character(
            name = name,
            race = race,
            race_level = 1,
            adventure_job = job,
            adventure_level = 1,
            profession_job = chosen_professions,
            profession_level = 1,
            attributes = attrs,
            )

    recalculate(character)

    pools = calculate_pools(character)

    character.current_hp = pools.hp[1]
    character.current_sanity = pools.sanity[1]
    character.current_stamina = pools.stamina[1]
    character.current_moxie = pools.moxie[1]
    character.current_fortune = pools.fortune[1]

    return character
