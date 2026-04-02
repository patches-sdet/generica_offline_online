import json
import os

from application.character_creation import create_character
from application.runtime import execute_ability

from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES

from domain.calculations import recalculate
from domain.content_registry import (
    initialize_content_registries,
    get_all_base_races,
    get_all_race_templates,
    get_all_adventure_jobs,
    get_all_profession_jobs,
)
from domain.race_resolution import MATERIAL_EFFECTS


initialize_content_registries()

PERSISTENCE_DIR = "src/persistence"


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


def choose_from_mapping(prompt, options_dict):
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_dict:
            return options_dict[choice]
        print("Invalid choice. Try again.")


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


def choose_job():
    jobs = get_all_adventure_jobs()

    print("Available Adventure Jobs:")
    valid_jobs = {}

    for job in jobs:
        bonuses = format_effects(job.effects_on_acquire)
        print(f"- {job.name} ({bonuses})")
        valid_jobs[job.name.lower()] = job.name

    return choose_from_mapping("Choose an adventure job: ", valid_jobs)


def choose_profession():
    professions = get_all_profession_jobs()

    print("Available Professions:")
    valid = {}

    for prof in professions:
        bonuses = format_effects(prof.effects_on_acquire)
        print(f"- {prof.name} ({bonuses})")
        valid[prof.name.lower()] = prof.name

    return choose_from_mapping("Choose a profession: ", valid)


def build_character():
    print("=== Generica Offline Character Creator ===\n")

    name = input("Enter character name: ").strip()
    while not name:
        name = input("Please enter a valid name: ").strip()

    base_race_names, race_template_name, material = choose_race_setup()
    adventure_job_name = choose_job()
    profession_job_name = choose_profession()

    print("\nSummary:")
    print(f"Name: {name}")
    print(f"Base Race(s): {', '.join(base_race_names)}")
    if race_template_name:
        print(f"Race Template: {race_template_name}")
    if material:
        print(f"Material: {material}")
    print(f"Adventure Job: {adventure_job_name}")
    print(f"Profession: {profession_job_name}")

    confirm = input("\nCreate this character? (y/n): ").strip().lower()
    if confirm != "y":
        print("Restarting character creation...\n")
        return build_character()

    character = create_character(
        name=name,
        base_race_names=base_race_names,
        race_template_name=race_template_name,
        material=material,
        adventure_job_names=[adventure_job_name],
        profession_job_names=[profession_job_name],
    )

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


def interaction_loop(character):
    should_save = False

    while True:
        debug_print_character(character)

        print("Options:")
        print("1. Use Ability")
        print("2. Rebuild Character State")
        print("3. Save & Exit")
        print("4. Exit Without Saving")

        choice = input("> ").strip()

        if choice == "1":
            handle_ability_use(character)

        elif choice == "2":
            recalculate(character)
            print("Character rebuilt.")

        elif choice == "3":
            should_save = True
            break

        elif choice == "4":
            confirm = input("Exit without saving? (y/n): ").strip().lower()
            if confirm == "y":
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