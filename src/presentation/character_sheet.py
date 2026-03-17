from domain.character import Character
from domain.attributes import Pools, Defenses

POOL_COLORS = {
        "hp": "\033[91m",       #Red
        "sanity": "\033[94m",   #Blue
        "stamina": "\033[92m",  #Green
        "moxie": "\033[95m",    #Magenta (eventually purple?)
        "fortune": "\033[93m"   #Yellow/Gold
        }

RESET_COLOR = "\033[0m"

def divider(title):
    print(f"\n--- {title.upper()} ---")

# Mapping to make the stats human-readable
PRETTY_NAMES = {
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
    "adventure_job": "Adventure Job",
    "adventure_level": "Adventure Lvl",
    "craft_job": "Craft Job",
    "craft_level": "Craft Lvl",
    "hp": "HP",
    "sanity": "Sanity",
    "stamina": "Stamina",
    "moxie": "Moxie",
    "fortune": "Fortune",
    "armor": "Armor",
    "mental_fortitude": "Mental Fortitude",
    "endurance": "Endurance",
    "cool": "Cool",
    "fate": "Fate"
}

def print_stat_block(title, stats:dict, hide_keys: list = None, color_map: dict=None):
    """
    This will print a block of stats in an RPG friendly format
    and supports optional coloring and current/max for pools.

    :param title: Title of the block
    :param stats: Dictionary of field names to values
                  For pools, the value should be a tuple (current, max)
    :param hide_keys: This can hide the keys from the above dict
    :param color_map: This can map pool field names to ANSI escape codes
    """

    if hide_keys is None:
        hide_keys = []

    if color_map is None:
        color_map = {}

    divider(title)
    for key, value in stats.items():
        if key in hide_keys:
            continue
        pretty_name = PRETTY_NAMES.get(key, key.replace("_", " ").title())
        color = color_map.get(key, "")
        
        # check for if the value is a pool tuple
        if isinstance(value, tuple) and len(value) == 2:
            current, maximum = value
            print(f"{color}{pretty_name}: {current}/{maximum}{RESET_COLOR}")
        else:
            if key == "material" and isinstance(value, str):
                value = value.capitalize()
            print(f"{color}{pretty_name}: {value}{RESET_COLOR}")

def debug_print_character(character):

    print("\n==============================")
    print(f"      CHARACTER SHEET")
    print("==============================")

    print(f"Name: {character.name}")
    race_line = character.attributes.race
    if character.attributes.race and character.attributes.race:
        if hasattr(character, "material") and character.material:
            race_line += f" ({character.material})"
    print(f"Race: {race_line}")
    print("\n==============================")
    print(f"      JOB(S)")
    print("==============================")

    # jobs with colors?
    print(f"Job: {character.job.name} ({character.job.job_class})")

    #attributes without color
    print_stat_block("Attributes", vars(character.attributes), hide_keys=["race"], color_map=None)

    #pools have colors because I'm extra
    print_stat_block("Pools", vars(character.pools), color_map=POOL_COLORS)

    #defenses are still plain and placeholder equations
    print_stat_block("Defenses", vars(character.defenses))

    print("==============================\n")
