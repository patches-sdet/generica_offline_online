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

# -------------------------
# HELPERS
# -------------------------

def divider(title):
    print(f"\n--- {title.upper()} ---")


def format_name(key, name_map):
    return name_map.get(key, key.replace("_", " ").title())


def format_source_name(source: str) -> str:
    if ":" in source:
        _, name = source.split(":", 1)
        return name
    return source


# -------------------------
# ATTRIBUTE BLOCK
# -------------------------

def print_attribute_block(character: Character):
    divider("Attributes")

    current = vars(character.attributes)
    base = getattr(character, "_base_attributes", {})
    sources = getattr(character, "_attribute_sources", {})

    for key, value in current.items():
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


# -------------------------
# GENERIC STAT BLOCK
# -------------------------

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


# -------------------------
# JOB DISPLAY
# -------------------------

def print_jobs(character: Character):
    print("\n==============================")
    print("         JOBS")
    print("==============================")

    # Adventure Jobs
    if character.adventure_jobs:
        print("Adventure Jobs:")
        for job in character.adventure_jobs:
            level = character.adventure_levels.get(job.name, 1)
            print(f"  - {job.name} (Lv. {level})")
    else:
        print("Adventure Jobs: None")

    # Profession Jobs
    if character.profession_jobs:
        print("\nProfessions:")
        for job in character.profession_jobs:
            level = character.profession_levels.get(job.name, 1)
            print(f"  - {job.name} (Lv. {level})")
    else:
        print("\nProfessions: None")


# -------------------------
# RACE DISPLAY
# -------------------------

def print_race(character: Character):
    race = character.race
    race_display = race.get_display_name()

    race_level = character.race_levels.get(race.name, 1)

    if race.base_race:
        base_name = race.base_race.name
        base_level = character.base_race_levels.get(base_name, 1)

        print(
            f"Race: {race_display} "
            f"(Lv. {race_level} / Base Lv. {base_level})"
        )
    else:
        print(f"Race: {race_display} (Lv. {race_level})")


# -------------------------
# SKILLS
# -------------------------

def print_skills(character: Character):
    divider("Skills")

    if not getattr(character, "skills", None):
        print("None")
        return

    for skill, level in sorted(character.skills.items()):
        print(f"{skill}: {level}")


# -------------------------
# ABILITIES
# -------------------------

def print_abilities(character: Character):
    print("\n==============================")
    print("        ABILITIES")
    print("==============================")

    if not character.abilities:
        print("None")
        return

    for ability in character.abilities:
        level = character.ability_levels.get(ability.name, 1)

        line = f"- {ability.name:<25} (Lv. {level})"

        if ability.cost:
            pool = ability.cost_pool or "resource"
            line += f" | Cost: {ability.cost} {pool.capitalize()}"

        if ability.duration:
            line += f" | Duration: {ability.duration}"

        print(line)

        if ability.description:
            print(f"    {ability.description}\n")


# -------------------------
# MAIN CHARACTER SHEET
# -------------------------

def debug_print_character(character: Character):

    print("\n==============================")
    print("      CHARACTER SHEET")
    print("==============================")

    print(f"Name: {character.name}")

    print_race(character)
    print_jobs(character)

    # Derived values
    pools = calculate_pools(character)
    defenses = calculate_defenses(character)

    # Stats
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

    # Skills (NEW)
    print_skills(character)

    # Abilities
    print_abilities(character)

    print("==============================\n")
