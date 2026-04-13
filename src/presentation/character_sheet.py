from dataclasses import asdict
from domain.character import Character
from domain.calculations import calculate_pools, calculate_defenses
from domain.content_registry import get_ability
from domain.race_resolution import get_race_display_name

POOL_COLORS = {
    "hp": "\033[91m",
    "sanity": "\033[94m",
    "stamina": "\033[92m",
    "moxie": "\033[95m",
    "fortune": "\033[93m",
}

RESET_COLOR = "\033[0m"

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

HIDDEN_SOURCES = {
    "roll",
}

SOURCE_ORDER_PREFIXES = (
    "race:",
    "adventure:",
    "profession:",
    "advanced:",
    "ability:",
    "equipment:",
    "inventory:",
    "active_effect:",
)


def divider(title):
    print(f"\n--- {title.upper()} ---")


def format_name(key, name_map):
    return name_map.get(key, key.replace("_", " ").title())


def format_source_name(source: str) -> str:
    if ":" in source:
        prefix, name = source.split(":", 1)

        if prefix == "race":
            return f"Race:{name}"
        if prefix == "adventure":
            return f"Job:{name}"
        if prefix == "profession":
            return f"Profession:{name}"
        if prefix == "advanced":
            return f"Advanced:{name}"
        if prefix == "ability":
            return f"Ability:{name}"
        if prefix == "equipment":
            return f"Equipment:{name}"
        if prefix == "inventory":
            return f"Inventory:{name}"
        if prefix == "active_effect":
            return f"Effect:{name}"

        return name

    return source.replace("_", " ").title()


def sort_sources_for_display(source_items):
    def source_rank(source_name: str) -> tuple[int, str]:
        for i, prefix in enumerate(SOURCE_ORDER_PREFIXES):
            if source_name.startswith(prefix):
                return (i, source_name)
        return (999, source_name)

    return sorted(source_items, key=lambda item: source_rank(item[0]))


def get_progression_entries(character: Character, ptype: str):
    progressions = getattr(character, "progressions", {}) or {}

    entries = []
    for (entry_type, entry_name), progression in progressions.items():
        if entry_type == ptype:
            entries.append((entry_name, progression))

    entries.sort(key=lambda item: item[0])
    return entries


def get_ability_objects(character: Character):
    abilities = getattr(character, "abilities", None)
    if abilities:
        return list(abilities)

    ability_levels = getattr(character, "ability_levels", {}) or {}
    resolved = []

    for ability_name in sorted(ability_levels):
        try:
            resolved.append(get_ability(ability_name))
        except Exception:
            continue

    return resolved


def print_attribute_block(character: Character):
    divider("Attributes")

    current = character.attributes.to_dict()
    base = getattr(character, "_base_attributes", {}) or {}
    sources = getattr(character, "_attribute_sources", {}) or {}

    for key in ATTRIBUTE_NAMES:
        value = current.get(key, 0)
        pretty_name = format_name(key, ATTRIBUTE_NAMES)

        base_value = base.get(key, value)
        attr_sources = sources.get(key, {}) or {}

        ordered_sources = sort_sources_for_display(attr_sources.items())

        parts = [
            f"{amount:+d} {format_source_name(source)}"
            for source, amount in ordered_sources
            if amount != 0
            and source not in HIDDEN_SOURCES
            and str(source).lower() != "base"
        ]

        if parts:
            breakdown = " | ".join(parts)
            print(f"{pretty_name}: {value} ({base_value} → {breakdown})")
        else:
            print(f"{pretty_name}: {value}")


def print_stat_block(title, stats: dict, name_map: dict, hide_keys=None, color_map=None):
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


def print_tags(character: Character):
    divider("Tags")

    tag_sets = {
        "General": getattr(character, "tags", set()) or set(),
        "Crafting": getattr(character, "crafting_tags", set()) or set(),
        "Gathering": getattr(character, "gathering_tags", set()) or set(),
        "Economic": getattr(character, "economic_tags", set()) or set(),
    }

    printed_any = False

    for category, tags in tag_sets.items():
        if tags:
            printed_any = True
            print(f"{category}: {', '.join(sorted(tags))}")

    if not printed_any:
        print("None")


def print_jobs(character: Character):
    divider("Jobs")

    adventure_entries = get_progression_entries(character, "adventure")
    profession_entries = get_progression_entries(character, "profession")
    advanced_entries = get_progression_entries(character, "advanced")

    if adventure_entries:
        print("Adventure Jobs:")
        for job_name, progression in adventure_entries:
            print(f"  - {job_name} (Lv. {progression.level})")
    else:
        print("Adventure Jobs: None")

    if profession_entries:
        print("\nProfessions:")
        for job_name, progression in profession_entries:
            print(f"  - {job_name} (Lv. {progression.level})")
    else:
        print("\nProfessions: None")

    if advanced_entries:
        print("\nAdvanced Jobs:")
        for job_name, progression in advanced_entries:
            print(f"  - {job_name} (Lv. {progression.level})")


def print_race(character: Character):
    race_display = get_race_display_name(character)

    race_entries = get_progression_entries(character, "race")
    if race_entries:
        levels = ", ".join(f"{name} Lv. {progression.level}" for name, progression in race_entries)
        print(f"Race: {race_display} [{levels}]")
    else:
        print(f"Race: {race_display}")


def print_skills(character: Character):
    divider("Skills")

    generic_skills = getattr(character, "skill_levels", {}) or {}

    ability_skills = {
        ability.name: getattr(character, "ability_levels", {}).get(ability.name, 1)
        for ability in getattr(character, "abilities", [])
        if getattr(ability, "is_skill", False)
    }

    if not generic_skills and not ability_skills:
        print("None")
        return

    if generic_skills:
        print("Generic Skills:")
        for skill, level in sorted(generic_skills.items()):
            print(f"{skill}: {level}")

    if ability_skills:
        if generic_skills:
            print()
        print("Ability Skills:")
        for skill, level in sorted(ability_skills.items()):
            print(f"{skill}: {level}")


def print_abilities(character: Character):
    divider("Abilities")

    abilities = get_ability_objects(character)

    if not abilities:
        print("None")
        return

    ability_levels = getattr(character, "ability_levels", {}) or {}

    def ability_sort_key(ability):
        return (
            getattr(ability, "is_passive", False),
            ability.name.lower(),
        )

    for ability in sorted(abilities, key=ability_sort_key):
        level = ability_levels.get(ability.name, 1)

        type_tag = "[Passive]" if getattr(ability, "is_passive", False) else "[Active]"
        skill_tag = "[Skill]" if getattr(ability, "is_skill", False) else ""

        line = f"- {ability.name:<25} {type_tag} {skill_tag} (Lv. {level})"

        cost = getattr(ability, "cost", 0)
        if cost:
            pool = getattr(ability, "cost_pool", None) or "resource"
            line += f" | Cost: {cost} {pool.capitalize()}"

        duration = getattr(ability, "duration", None)
        if duration:
            line += f" | Duration: {duration}"

        print(line)

        description = getattr(ability, "description", "")
        if description:
            print(f"    {description}\n")

def debug_print_character(character: Character):
    divider("Character Sheet")

    print(f"Name: {character.name}")

    print_race(character)
    print_jobs(character)

    pools = calculate_pools(character)
    defenses = calculate_defenses(character)

    print_attribute_block(character)

    print_stat_block(
        "Pools",
        asdict(pools),
        POOL_NAMES,
        color_map=POOL_COLORS,
    )

    print_stat_block(
        "Defenses",
        asdict(defenses),
        name_map=DEFENSE_NAMES,
    )

    print_tags(character)
    print_skills(character)
    print_abilities(character)

    print("==============================\n")