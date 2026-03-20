from domain.character import Character
from domain.calculations import calculate_pools, calculate_defenses
from domain.abilities import Ability

# COLORS

POOL_COLORS = {
    "hp": "\033[91m",       # Red
    "sanity": "\033[94m",   # Blue
    "stamina": "\033[92m",  # Green
    "moxie": "\033[95m",    # Magenta
    "fortune": "\033[93m"   # Yellow
}

RESET_COLOR = "\033[0m"

# DISPLAY NAME MAPPINGS

ATTRIBUTE_NAMES = {
    "strength": "STR",
    "constitution": "CON",
    "intelligence": "INT",
    "wisdom": "WIS",
    "dexterity": "DEX",
    "agility": "AGI",
    "charisma": "CHA",
    "willpower": "WIL",
    "perception": "PER",
    "luck": "LUK",
}

POOL_NAMES = {
    "hp": "HP",
    "sanity": "Sanity",
    "stamina": "Stamina",
    "moxie": "Moxie",
    "fortune": "Fortune",
}

DEFENSE_NAMES = {
    "armor": "Armor",
    "mental_fortitude": "Mental Fortitude",
    "endurance": "Endurance",
    "cool": "Cool",
    "fate": "Fate",
}


# HELPERS

def divider(title):
    print(f"\n--- {title.upper()} ---")


def format_name(key, name_map):
    return name_map.get(key, key.replace("_", " ").title())


# stat block printer

def print_attribute_block(character: Character):
    divider("Attributes")

    current = vars(character.attributes)
    base = getattr(character, "_base_attributes", {})

    for key, value in current.items():
        if key in ["race", "material"]:
            continue

        pretty_name = format_name(key, ATTRIBUTE_NAMES)

        base_value = base.get(key, value)
        delta = value - base_value

        if delta != 0:
            print(f"{pretty_name}: {value} ({base_value} {'+' if delta > 0 else ''}{delta})")
        else:
            print(f"{pretty_name}: {value}")

def print_stat_block(title, stats: dict, name_map: dict,
                     hide_keys: list = None, color_map: dict = None):

    if hide_keys is None:
        hide_keys = []

    if color_map is None:
        color_map = {}

    divider(title)

    for key, value in stats.items():
        if key in hide_keys:
            continue

        pretty_name = format_name(key, name_map)
        color = color_map.get(key, "")

        # Pool tuple handling
        if isinstance(value, tuple) and len(value) == 2:
            current, maximum = value
            print(f"{color}{pretty_name}: {current}/{maximum}{RESET_COLOR}")
        else:
            if key == "material" and isinstance(value, str):
                value = value.capitalize()

            print(f"{color}{pretty_name}: {value}{RESET_COLOR}")


# MAIN CHARACTER SHEET

def debug_print_character(character: Character):

    print("\n==============================")
    print("      CHARACTER SHEET")
    print("==============================")

    print(f"Name: {character.name}")

    # ----------------------
    # Race
    # ----------------------
    race_line = character.race.name

    if character.race.material:
        race_line += f" ({character.race.material.capitalize()})"

    print(f"Race: {race_line} (Lv. {character.race_level})")

    # ----------------------
    # Jobs
    # ----------------------
    print("\n==============================")
    print("         JOBS")
    print("==============================")

    print(
        f"Adventure Job: "
        f"{character.adventure_job.name} "
        f"Lv. {character.adventure_level}"
    )

    if character.profession_job:
        print(
            f"Profession: "
            f"{character.profession_job.name} "
            f"Lv. {character.profession_level}"
        )
    else:
        print("Profession: None")

    # ----------------------
    # Derived Values
    # ----------------------
    pools = calculate_pools(character)
    defenses = calculate_defenses(character)

    # ----------------------
    # Stats
    # ----------------------

    print_attribute_block(character)

    print_stat_block(
        "Pools",
        vars(pools),
        POOL_NAMES,
        color_map=POOL_COLORS
    )

    print_stat_block(
        "Defenses",
        vars(defenses),
        DEFENSE_NAMES
    )

    print("\n==============================")
    print("        ABILITIES")
    print("==============================")

    if hasattr(character, "abilities") and character.abilities:
        for ability in character.abilities:
            level = 1

            if hasattr(character, "ability_levels"):
                level = character.ability_levels.get(ability.name, 1)
            print(f"- {ability.name:<25} (Lv. {level})")
    else:
        print("None")

    print("==============================\n")
