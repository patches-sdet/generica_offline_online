import json
import os

from application.character_creation import create_character, MATERIAL_EFFECTS
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.race import RACES, resolve_race
from domain.adventure import get_jobs_grouped_by_class, resolve_job
from domain.profession import get_all_professions, resolve_profession
from domain.effects import StatIncrease
from domain.runtime import execute_ability
from domain.calculations import recalculate

PERSISTENCE_DIR = "src/persistence"


# -------------------------
# HELPERS
# -------------------------

def format_effects(effects):
    parts = []

    for effect in effects:
        if isinstance(effect, StatIncrease):
            stat_name = ATTRIBUTE_NAMES.get(effect.stat, effect.stat.upper())
            parts.append(f"+{effect.amount} {stat_name}")

    return ", ".join(parts)


def choose_from_mapping(prompt, options_dict):
    """
    options_dict: {normalized_key: display_value}
    """
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_dict:
            return options_dict[choice]
        print("Invalid choice. Try again.")


# -------------------------
# RACE SELECTION
# -------------------------

def choose_race():
    print("Available races:")
    for r_name in sorted(RACES.keys()):
        print(f"- {r_name}")

    race_lookup = {r.lower(): r for r in RACES.keys()}

    race_input = choose_from_mapping("Choose a race: ", race_lookup)
    race = resolve_race(race_input)

    base_race = None
    material = None

    if race.requires_material:
        print("\nThis race requires a base race and material.")

        # Base races
        print("\nAvailable base races:")
        base_race_lookup = {
            r.name.lower(): r.name
            for r in RACES.values()
            if r.can_be_base
        }

        for name in base_race_lookup.values():
            print(f"- {name}")

        base_race_name = choose_from_mapping(
            "Choose base race: ",
            base_race_lookup
        )
        base_race = resolve_race(base_race_name)

        # Materials
        print("\nAvailable materials:")
        material_lookup = {
            m.lower(): m for m in MATERIAL_EFFECTS.keys()
        }

        for mat in MATERIAL_EFFECTS.keys():
            print(f"- {mat}")

        material = choose_from_mapping(
            "Choose material: ",
            material_lookup
        )

    return race, base_race, material


# -------------------------
# JOB SELECTION
# -------------------------

def choose_job():
    jobs_by_class = get_jobs_grouped_by_class()

    print("Available Jobs:")
    valid_jobs = {}

    for job_class in sorted(jobs_by_class.keys()):
        print(f"{job_class}:")
        for job in jobs_by_class[job_class]:
            bonuses = format_effects(job.effects_on_acquire)
            print(f"  - {job.name} ({bonuses})")
            valid_jobs[job.name.lower()] = job.name

    job_input = choose_from_mapping("Choose a job: ", valid_jobs)
    return resolve_job(job_input)


# -------------------------
# PROFESSION SELECTION
# -------------------------

def choose_profession():
    professions = get_all_professions()

    print("Available Professions:")
    valid_professions = {}

    for prof in professions:
        bonuses = format_effects(prof.effects_on_acquire)
        print(f"- {prof.name} ({bonuses})")
        valid_professions[prof.name.lower()] = prof.name

    profession_input = choose_from_mapping(
        "Choose a profession: ",
        valid_professions
    )

    return resolve_profession(profession_input)


# -------------------------
# CHARACTER CREATION
# -------------------------

def build_character():
    print("=== Generica Offline Character Creator ===\n")

    # Name
    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    # Race
    race, base_race, material = choose_race()

    # Job
    job = choose_job()

    # Profession
    profession = choose_profession()

    # Validation (defensive, optional)
    if base_race is not None and not hasattr(base_race, "name"):
        raise TypeError(f"base_race must be Race, got {type(base_race)}")

    character = create_character(
        char_name,
        race=race,
        jobs=[job],
        professions=[profession],
        base_race=base_race,
        material=material
    )

    print("=== Character Created ===")
    return character


# -------------------------
# GAME LOOP
# -------------------------

def interaction_loop(character):
    should_save = False

    while True:
        debug_print_character(character)

        print("Options:")
        print("1. Use Ability")
        print("2. Refresh Character")
        print("3. Save & Exit")
        print("4. Exit Without Saving")

        choice = input("> ").strip()

        if choice == "1":
            handle_ability_use(character)

        elif choice == "2":
            recalculate(character)
            print("Character recalculated.")

        elif choice == "3":
            should_save = True
            break

        elif choice == "4":
            confirm = input("Exit without saving? (y/n): ").strip().lower()
            if confirm == "y":
                should_save = False
                break

        else:
            print("Invalid option.")

    return should_save


# -------------------------
# ABILITY HANDLER
# -------------------------

def handle_ability_use(character):
    if not character.abilities:
        print("No abilities available.")
        return

    print("Available Abilities:")
    for i, ability in enumerate(character.abilities, 1):
        print(f"{i}. {ability.name}")

    ability_choice = input("Choose ability #: ").strip()

    if not ability_choice.isdigit():
        print("Invalid input.")
        return

    index = int(ability_choice) - 1

    if not (0 <= index < len(character.abilities)):
        print("Invalid selection.")
        return

    ability = character.abilities[index]

    try:
        execute_ability(character, ability.name)
    except Exception as e:
        print(f"Error: {e}")


# -------------------------
# SAVE
# -------------------------

def save_character(character):
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)

    filename = f"{character.name.replace(' ', '_').lower()}_character.json"
    filepath = os.path.join(PERSISTENCE_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(character.to_dict(), f, indent=4)

    print(f"Character saved to: {filename}")


# -------------------------
# ENTRY POINT
# -------------------------

def main():
    character = build_character()

    should_save = interaction_loop(character)

    if should_save:
        save_character(character)
    else:
        print("Exited without saving.")


if __name__ == "__main__":
    main()
