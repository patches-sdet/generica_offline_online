import os, json
from application.character_creation import (
    create_character,
    apply_generic_skill_allocation,
)
from application.runtime import execute_ability
from application.leveling import (
    award_level_points,
    award_grind_points,
    level_up_progression,
    level_adventure_job,
    level_profession_job,
    level_race_progression,
    level_advanced_job,
    learn_new_adventure_job,
    learn_new_advanced_job,
    grind_skill,
    grind_attribute,
)
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.calculations import recalculate
from domain.content_registry import (
    initialize_content_registries,
    get_all_base_races,
    get_all_race_templates,
    get_all_adventure_jobs,
    get_all_profession_jobs,
    get_all_advanced_jobs,
)
from domain.race_resolution import MATERIAL_EFFECTS

initialize_content_registries()

PERSISTENCE_DIR = "src/persistence"
CREATION_ATTRIBUTE_POINTS = 50
CREATION_ADVENTURE_LEVELS = 7
CREATION_PROFESSION_LEVELS = 5
CREATION_SKILL_POINTS = 100
GENERIC_SKILL_NAMES = [
    "Archery",
    "Axes",
    "Brawling",
    "Climb",
    "Clubs",
    "Dagger",
    "Dodge",
    "Fishing",
    "Flight",
    "Guns",
    "Lockpicking",
    "Riding",
    "Shields",
    "Siege",
    "Spear",
    "Stealth",
    "Swim",
    "Swords",
    "Throwing",
    "Whips",
]

def format_effects(effects):
    parts = []

    for effect in effects:
        if hasattr(effect, "stats"):
            for stat, value in effect.stats.items():
                name = ATTRIBUTE_NAMES.get(stat, stat.title())
                parts.append(f"{value:+d} {name}")

        elif hasattr(effect, "stat") and hasattr(effect, "amount"):
            name = ATTRIBUTE_NAMES.get(effect.stat, effect.stat.title())
            parts.append(f"{effect.amount:+d} {name}")

    return ", ".join(parts)

def prompt_int(prompt, *, minimum=0, maximum=None):
    while True:
        raw = input(prompt).strip()

        if not raw.isdigit():
            print("Enter a whole number.")
            continue

        value = int(raw)

        if value < minimum:
            print(f"Value must be at least {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Value must be no more than {maximum}.")
            continue

        return value

def choose_from_mapping(prompt, options_dict):
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_dict:
            return options_dict[choice]
        print("Invalid choice. Try again.")

def confirm(prompt="Confirm? (y/n): "):
    return input(prompt).strip().lower() == "y"

def choose_race_setup():
    base_races = get_all_base_races()
    race_templates = get_all_race_templates()

    print("Available base races:")
    base_lookup = {}
    for race in base_races:
        print(f"- {race.name}")
        base_lookup[race.name.lower()] = race.name

    first_base = choose_from_mapping("Choose a base race: ", base_lookup)
    base_race_names = [first_base]

    print("\nAvailable race templates:")
    print("- none")
    template_lookup = {"none": None}

    for template in race_templates:
        print(f"- {template.name}")
        template_lookup[template.name.lower()] = template.name

    race_template_name = choose_from_mapping(
        "Choose a race template (or none): ",
        template_lookup,
    )

    material = None

    if race_template_name == "Crossbreed":
        second_base = choose_from_mapping("Choose second base race: ", base_lookup)
        base_race_names.append(second_base)

    if race_template_name is not None:
        selected_template = next(t for t in race_templates if t.name == race_template_name)

        if getattr(selected_template, "requires_material", False):
            print("\nAvailable materials:")
            material_lookup = {}

            for mat in MATERIAL_EFFECTS:
                print(f"- {mat}")
                material_lookup[mat.lower()] = mat

            material = choose_from_mapping("Choose material: ", material_lookup)

    return base_race_names, race_template_name, material

def print_adventure_jobs():
    print("Available Adventure Jobs:")
    for job in get_all_adventure_jobs():
        bonuses = format_effects(job.effects_on_acquire)
        suffix = f" ({bonuses})" if bonuses else ""
        print(f"- {job.name}{suffix}")

def print_professions():
    print("Available Professions:")
    for prof in get_all_profession_jobs():
        bonuses = format_effects(prof.effects_on_acquire)
        suffix = f" ({bonuses})" if bonuses else ""
        print(f"- {prof.name}{suffix}")

def print_advanced_jobs():
    print("Available Advanced Jobs:")
    for job in get_all_advanced_jobs():
        print(f"- {job.name}")

def get_adventure_job_lookup():
    return {job.name.lower(): job.name for job in get_all_adventure_jobs()}

def get_profession_lookup():
    return {prof.name.lower(): prof.name for prof in get_all_profession_jobs()}

def get_advanced_job_lookup():
    return {job.name.lower(): job.name for job in get_all_advanced_jobs()}

def allocate_total_levels(label, total_levels, lookup, printer):
    allocations = {}
    remaining = total_levels

    print(f"\nAllocate {total_levels} total {label} levels.")
    print("You may split these across multiple choices.")

    while remaining > 0:
        print(f"\nRemaining {label} levels: {remaining}")
        printer()

        name = choose_from_mapping(f"Choose {label}: ", lookup)
        amount = prompt_int(
            f"How many levels for {name}? ",
            minimum=1,
            maximum=remaining,
        )

        allocations[name] = allocations.get(name, 0) + amount
        remaining -= amount

    return allocations

def allocate_creation_attributes():
    allocations = {}
    remaining = CREATION_ATTRIBUTE_POINTS
    valid_stats = set(ATTRIBUTE_NAMES.keys())

    print(f"\nAllocate {CREATION_ATTRIBUTE_POINTS} attribute points.")
    print("You may place points in any stat, in any increment.")

    while remaining > 0:
        print(f"\nRemaining attribute points: {remaining}")
        print("Available stats:")
        for stat, display in ATTRIBUTE_NAMES.items():
            current = allocations.get(stat, 0)
            suffix = f" (+{current})" if current else ""
            print(f"- {stat} ({display}){suffix}")

        stat = input("Choose stat: ").strip().lower()

        if stat not in valid_stats:
            print("Invalid stat.")
            continue

        amount = prompt_int(
            f"Add how many points to {stat}? ",
            minimum=1,
            maximum=remaining,
        )

        allocations[stat] = allocations.get(stat, 0) + amount
        remaining -= amount

    return allocations

def get_known_skill_names():
    return sorted(GENERIC_SKILL_NAMES)

def allocate_creation_skills():
    allocations = {}
    remaining = CREATION_SKILL_POINTS

    print(f"\nAllocate {CREATION_SKILL_POINTS} skill points.")
    print("You may enter a listed skill or type a custom skill name.")

    while remaining > 0:
        print(f"\nRemaining skill points: {remaining}")

        known_skills = get_known_skill_names()
        if known_skills:
            print("Known skills:")
            for skill_name in known_skills:
                current = allocations.get(skill_name, 0)
                suffix = f" (+{current})" if current else ""
                print(f"- {skill_name}{suffix}")

        if allocations:
            print("\nCurrent allocations:")
            for skill_name, amount in sorted(allocations.items()):
                print(f"- {skill_name}: {amount}")

        skill_lookup = {name.lower(): name for name in get_known_skill_names()}

        choice = input("Skill name: ").strip().lower()

        if choice not in skill_lookup:
            print("Invalid generic skill. Choose from the listed generic skills.")
            continue

        skill_name = skill_lookup[choice]

        amount = prompt_int(
            f"Add how many points to {skill_name}? ",
            minimum=1,
            maximum=remaining,
        )

        allocations[skill_name] = allocations.get(skill_name, 0) + amount
        remaining -= amount

    return allocations

def apply_creation_target_levels(character, adventure_allocations, profession_allocations):
    """
    create_character() registers each selected job/profession at level 1.
    Creation allocation should therefore apply only the extra levels beyond 1.
    This does not spend level points.
    """
    for job_name, target_level in adventure_allocations.items():
        extra_levels = target_level - 1
        if extra_levels > 0:
            level_up_progression(
                character,
                ptype="adventure",
                name=job_name,
                amount=extra_levels,
                refill_pools=False,
            )

    for profession_name, target_level in profession_allocations.items():
        extra_levels = target_level - 1
        if extra_levels > 0:
            level_up_progression(
                character,
                ptype="profession",
                name=profession_name,
                amount=extra_levels,
                refill_pools=False,
            )

    recalculate(character)

def build_character():
    print("=== Generica Offline Character Creator ===\n")

    name = input("Enter character name: ").strip()
    while not name:
        name = input("Please enter a valid name: ").strip()

    base_race_names, race_template_name, material = choose_race_setup()

    adventure_allocations = allocate_total_levels(
        "adventure job",
        CREATION_ADVENTURE_LEVELS,
        get_adventure_job_lookup(),
        print_adventure_jobs,
    )

    profession_allocations = allocate_total_levels(
        "profession",
        CREATION_PROFESSION_LEVELS,
        get_profession_lookup(),
        print_professions,
    )

    attribute_allocations = allocate_creation_attributes()
    skill_allocations = allocate_creation_skills()

    print("\nSummary:")
    print(f"Name: {name}")
    print(f"Base Race(s): {', '.join(base_race_names)}")

    if race_template_name:
        print(f"Race Template: {race_template_name}")
    if material:
        print(f"Material: {material}")

    print("\nAdventure Jobs:")
    for job_name, level in adventure_allocations.items():
        print(f"- {job_name} Lv. {level}")

    print("\nProfessions:")
    for profession_name, level in profession_allocations.items():
        print(f"- {profession_name} Lv. {level}")

    print("\nAttribute Allocation:")
    for stat, amount in sorted(attribute_allocations.items()):
        print(f"- {stat}: +{amount}")

    print("\nSkill Allocation:")
    for skill_name, amount in sorted(skill_allocations.items()):
        print(f"- {skill_name}: +{amount}")

    if not confirm("\nCreate this character? (y/n): "):
        print("Restarting character creation...\n")
        return build_character()

    character = create_character(
        name=name,
        base_race_names=base_race_names,
        race_template_name=race_template_name,
        material=material,
        adventure_job_names=list(adventure_allocations.keys()),
        profession_job_names=list(profession_allocations.keys()),
        manual_attribute_allocations=attribute_allocations,
    )

    apply_creation_target_levels(
        character,
        adventure_allocations,
        profession_allocations,
    )

    apply_generic_skill_allocation(character, skill_allocations)

    recalculate(character)

    print("\n=== Character Created ===")
    return character

def get_activatable_abilities(character):
    return [
        ability
        for ability in getattr(character, "abilities", [])
        if not getattr(ability, "is_passive", False)
    ]

def handle_ability_use(character):
    active_abilities = get_activatable_abilities(character)

    if not active_abilities:
        print("No active abilities available.")
        return

    print("Available Active Abilities:")
    for i, ability in enumerate(active_abilities, 1):
        details = []

        if getattr(ability, "is_skill", False):
            details.append("Skill")

        if getattr(ability, "cost", 0):
            pool = getattr(ability, "cost_pool", None) or "resource"
            details.append(f"Cost: {ability.cost} {pool.capitalize()}")

        if getattr(ability, "duration", None):
            details.append(f"Duration: {ability.duration}")

        suffix = f" [{' | '.join(details)}]" if details else ""
        print(f"{i}. {ability.name}{suffix}")

    choice = input("Choose ability #: ").strip()

    if not choice.isdigit():
        print("Invalid input.")
        return

    idx = int(choice) - 1
    if not (0 <= idx < len(active_abilities)):
        print("Invalid selection.")
        return

    ability = active_abilities[idx]

    try:
        execute_ability(character, ability.name)
        print(f"{ability.name} resolved.")
    except Exception as e:
        print(f"Error: {e}")

def choose_progression_by_type(character, ptype):
    progressions = character.get_progressions_by_type(ptype)

    if not progressions:
        print(f"No {ptype} progressions available.")
        return None

    print(f"Available {ptype} progressions:")
    for i, progression in enumerate(progressions, 1):
        print(f"{i}. {progression.name} Lv. {progression.level}")

    idx = prompt_int("Choose #: ", minimum=1, maximum=len(progressions)) - 1
    return progressions[idx]

def handle_award_level_points(character):
    amount = prompt_int("Award how many level points? ", minimum=1)
    award_level_points(character, amount)
    print(f"Awarded {amount} level point(s). Total: {character.level_points}")

def handle_award_grind_points(character):
    amount = prompt_int("Award how many grind points? ", minimum=1)
    award_grind_points(character, amount)
    print(f"Awarded {amount} grind point(s). Total: {character.grind_points}")

def handle_level_adventure(character):
    progression = choose_progression_by_type(character, "adventure")
    if progression is None:
        return

    try:
        level_adventure_job(character, progression.name)
    except Exception as e:
        print(f"Error: {e}")

def handle_level_profession(character):
    progression = choose_progression_by_type(character, "profession")
    if progression is None:
        return

    try:
        level_profession_job(character, progression.name)
    except Exception as e:
        print(f"Error: {e}")

def handle_level_race(character):
    progression = choose_progression_by_type(character, "race")
    if progression is None:
        return

    try:
        level_race_progression(character, progression.name)
    except Exception as e:
        print(f"Error: {e}")

def handle_level_advanced(character):
    progression = choose_progression_by_type(character, "advanced")
    if progression is None:
        return

    try:
        level_advanced_job(character, progression.name)
    except Exception as e:
        print(f"Error: {e}")

def handle_learn_new_adventure(character):
    print_adventure_jobs()
    job_name = choose_from_mapping(
        "Choose new adventure job: ",
        get_adventure_job_lookup(),
    )

    try:
        learn_new_adventure_job(character, job_name)
    except Exception as e:
        print(f"Error: {e}")

def handle_learn_new_advanced(character):
    print_advanced_jobs()
    job_name = choose_from_mapping(
        "Choose new advanced job: ",
        get_advanced_job_lookup(),
    )

    try:
        learn_new_advanced_job(character, job_name)
    except Exception as e:
        print(f"Error: {e}")

def handle_grind_skill(character):
    if not character.skill_levels:
        print("Character has no skills to grind.")
        return

    print("Current skills:")
    skills = sorted(character.skill_levels.items())

    for i, (skill_name, level) in enumerate(skills, 1):
        print(f"{i}. {skill_name} Lv. {level}")

    idx = prompt_int("Choose skill #: ", minimum=1, maximum=len(skills)) - 1
    skill_name = skills[idx][0]

    try:
        grind_skill(character, skill_name)
    except Exception as e:
        print(f"Error: {e}")

def handle_grind_attribute(character):
    print("Available attributes:")
    stats = list(ATTRIBUTE_NAMES.keys())

    for i, stat in enumerate(stats, 1):
        display = ATTRIBUTE_NAMES.get(stat, stat.title())
        print(f"{i}. {display}: {character.get_stat(stat)}")

    idx = prompt_int("Choose attribute #: ", minimum=1, maximum=len(stats)) - 1
    stat = stats[idx]

    try:
        grind_attribute(character, stat)
    except Exception as e:
        print(f"Error: {e}")

def handle_free_table_attribute_award(character):
    """
    Manual table adjustment that does not spend grind points.
    Useful for GM-awarded creation corrections or table rulings.
    """
    print("Available attributes:")
    stats = list(ATTRIBUTE_NAMES.keys())

    for i, stat in enumerate(stats, 1):
        display = ATTRIBUTE_NAMES.get(stat, stat.title())
        print(f"{i}. {display}: {character.get_stat(stat)}")

    idx = prompt_int("Choose attribute #: ", minimum=1, maximum=len(stats)) - 1
    stat = stats[idx]

    amount = prompt_int("Add how many points? ", minimum=1)

    character.add_manual_attribute_increase(
        stat,
        amount,
        source="table:manual",
    )
    recalculate(character)

    print(f"Added {amount} point(s) to {stat}.")

def handle_free_table_skill_award(character):
    print("Generic skills:")
    for skill_name in get_known_skill_names():
        print(f"- {skill_name}")

    skill_lookup = {name.lower(): name for name in get_known_skill_names()}

    choice = input("Skill name: ").strip().lower()

    if choice not in skill_lookup:
        print("Invalid generic skill. Choose from the listed generic skills.")
        return

    skill_name = skill_lookup[choice]
    amount = prompt_int("Add how many points? ", minimum=1)

    apply_generic_skill_allocation(character, {skill_name: amount})
    print(f"Added {amount} point(s) to {skill_name}.")

def handle_leveling_menu(character):
    while True:
        print("\nLeveling / Advancement")
        print(f"Level Points: {character.level_points}")
        print(f"Grind Points: {character.grind_points}")
        print("1. Award Level Points")
        print("2. Award Grind Points")
        print("3. Level Adventure Job")
        print("4. Level Profession")
        print("5. Level Race Progression")
        print("6. Level Advanced Job")
        print("7. Learn New Adventure Job")
        print("8. Learn New Advanced Job")
        print("9. Grind Skill")
        print("10. Grind Attribute")
        print("11. Free Table Attribute Award")
        print("12. Free Table Skill Award")
        print("13. Back")

        choice = input("> ").strip()

        if choice == "1":
            handle_award_level_points(character)
        elif choice == "2":
            handle_award_grind_points(character)
        elif choice == "3":
            handle_level_adventure(character)
        elif choice == "4":
            handle_level_profession(character)
        elif choice == "5":
            handle_level_race(character)
        elif choice == "6":
            handle_level_advanced(character)
        elif choice == "7":
            handle_learn_new_adventure(character)
        elif choice == "8":
            handle_learn_new_advanced(character)
        elif choice == "9":
            handle_grind_skill(character)
        elif choice == "10":
            handle_grind_attribute(character)
        elif choice == "11":
            handle_free_table_attribute_award(character)
        elif choice == "12":
            handle_free_table_skill_award(character)
        elif choice == "13":
            return
        else:
            print("Invalid option.")

def interaction_loop(character):
    should_save = False

    while True:
        debug_print_character(character)

        print("Options:")
        print("1. Use Ability")
        print("2. Rebuild Character State")
        print("3. Leveling / Advancement")
        print("4. Save & Exit")
        print("5. Exit Without Saving")

        choice = input("> ").strip()

        if choice == "1":
            handle_ability_use(character)

        elif choice == "2":
            recalculate(character)
            print("Character rebuilt.")

        elif choice == "3":
            handle_leveling_menu(character)

        elif choice == "4":
            should_save = True
            break

        elif choice == "5":
            if confirm("Exit without saving? (y/n): "):
                break

        else:
            print("Invalid option.")

    return should_save

def save_character(character):
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)

    filename = f"{character.name.replace(' ', '_').lower()}_character.json"
    path = os.path.join(PERSISTENCE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(character.to_dict(), f, indent=4)

    print(f"Character saved to: {path}")

def run_cli():
    character = build_character()

    should_save = interaction_loop(character)

    if should_save:
        save_character(character)
    else:
        print("Exited without saving.")

if __name__ == "__main__":
    run_cli()