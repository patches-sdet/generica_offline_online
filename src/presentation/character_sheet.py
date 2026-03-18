from domain.character import Character

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

    race_line = character.race.name

    if character.race.material:
        race_line += f" ({character.race.material.capitalize()})"

    print(f"Race: {race_line}")

    print("\n==============================")
    print("      JOB(S)")
    print("==============================")

    print(f"Job: {character.adventure_job.name} ({character.adventure_job.job_class})")

    # STAT BLOCKS

    print_stat_block(
        "Attributes",
        vars(character.attributes),
        ATTRIBUTE_NAMES,
        hide_keys=["race", "material"]
    )

    print_stat_block(
        "Pools",
        vars(character.pools),
        POOL_NAMES,
        color_map=POOL_COLORS
    )

    print_stat_block(
        "Defenses",
        vars(character.defenses),
        DEFENSE_NAMES
    )

    print("==============================\n")
