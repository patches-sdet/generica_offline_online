from domain.character import Character
from domain.calculations import calculate_pools, calculate_defenses

# COLORS

POOL_COLORS = {
    "hp": "\033[91m",
    "sanity": "\033[94m",
    "stamina": "\033[92m",
    "moxie": "\033[95m",
    "fortune": "\033[93m"
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

def format_source_name(source: str) -> str:
    if ":" in source:
        _, name = source.split(":", 1)
        return name
    return source

# ATTRIBUTE BLOCK

def print_attribute_block(character: Character):
    divider("Attributes")

    current = vars(character.attributes)
    base = getattr(character, "_base_attributes", {})
    sources = getattr(character, "_attribute_sources", {})

    for key, value in current.items():
        if key in ["race", "material"]:
            continue

        pretty_name = format_name(key, ATTRIBUTE_NAMES)

        base_value = base.get(key, value)
        attr_sources = sources.get(key, {})

        parts = []
        for source, amount in attr_sources.items():
            if amount != 0:
                parts.append(f"{amount:+d} {format_source_name(source)}")

        if parts:
            breakdown = " ".join(parts)
            print(f"{pretty_name}: {value} ({base_value} {breakdown})")
        else:
            print(f"{pretty_name}: {value}")

# GENERIC STAT BLOCK

def print_stat_block(title, stats: dict, name_map: dict,
                     hide_keys=None, color_map=None):

    hide_keys = hide_keys or []
    color_map = color_map or {}

    divider(title)

    for key, value in stats.items():
        if key in hide_keys:
            continue

        pretty_name = format_name(key, name_map)
        color = color_map.get(key, "")

        if isinstance(value, tuple) and len(value) == 2:
            current, maximum = value
            print(f"{color}{pretty_name}: {current}/{maximum}{RESET_COLOR}")
        else:
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

    print(f"Race: {race_line} (Lv. {character.race_level})")

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

    # DERIVED VALUES

    pools = calculate_pools(character)
    defenses = calculate_defenses(character)

    # STATS

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

    if character.abilities:
        for ability in character.abilities:
            level = character.ability_levels.get(ability.name, 1)

            line = f"- {ability.name:<25} (Lv. {level})"

            cost = getattr(ability, "cost", None)
            cost_pool = getattr(ability, "cost_pool", None)
            duration = getattr(ability, "duration", None)
            description = getattr(ability, "description", None)

            if cost:
                if cost_pool:
                    line += f" | Cost: {cost} {cost_pool.capitalize()}"
                else:
                    line += f" | Cost: {cost}"

            if duration:
                line += f" | Duration: {duration}"

            print(line)

            if description:
                print(f"    {description}\n")
    else:
        print("None")

    print("==============================\n")
