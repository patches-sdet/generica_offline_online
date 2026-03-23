import json
import os

from application.character_creation import create_character
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.race import RACES
from domain.adventure import get_jobs_grouped_by_class
from domain.profession import get_all_professions
from domain.effects import StatIncrease
from domain.runtime import execute_ability

PERSISTENCE_DIR = "src/persistence"


# -------------------------
# Helpers
# -------------------------

def format_effects(effects):
    parts = []

    for effect in effects:
        if isinstance(effect, StatIncrease):
            stat_name = ATTRIBUTE_NAMES.get(effect.stat, effect.stat.upper())
            parts.append(f"+{effect.amount} {stat_name}")

    return ", ".join(parts)


def choose_from_list(prompt, valid_options):
    while True:
        choice = input(prompt).strip()
        if choice.lower() in valid_options:
            return choice
        print("Invalid choice. Try again.")


# -------------------------
# MAIN
# -------------------------

def main():
    print("=== Tabletop RPG Character Creator ===\n")

    # -------------------------
    # NAME
    # -------------------------

    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    # -------------------------
    # RACE
    # -------------------------

    print("Available races:")
    for race_name in sorted(RACES.keys()):
        print(f"- {race_name}")

    race_lookup = {r.lower(): r for r in RACES.keys()}

    race_input = choose_from_list(
        "Choose a race: ",
        race_lookup.keys()
    )

    race_name = race_lookup[race_input.lower()]

    # -------------------------
    # JOB
    # -------------------------

    jobs_by_class = get_jobs_grouped_by_class()
    print("Available Jobs:")

    valid_jobs = {}

    for job_class in sorted(jobs_by_class.keys()):
        print(f"{job_class}:")
        for job in jobs_by_class[job_class]:
            bonuses = format_effects(job.effects_on_acquire)
            print(f"  - {job.name} ({bonuses})")

            valid_jobs[job.name.lower()] = job.name

    job_input = choose_from_list(
        "Choose a job: ",
        valid_jobs.keys()
    )

    job_name = valid_jobs[job_input.lower()]

    # Professions

    professions = get_all_professions()

    print("Available Professions:")

    valid_professions = {}

    for prof in professions:
        bonuses = format_effects(prof.effects_on_acquire)
        print(f"- {prof.name} ({bonuses})")
        valid_professions[prof.name.lower()] = prof.name

    profession_input = choose_from_list(
            "Choose a profession: ",
             valid_professions.keys()
            )

    profession_name = valid_professions[profession_input.lower()]

    # -------------------------
    # CREATE CHARACTER
    # -------------------------

    character = create_character(char_name, race_name, job_name, profession_name)

    print("=== Character Created ===")

    # -------------------------
    # INTERACTION LOOP
    # -------------------------

    while True:
        debug_print_character(character)

        print("Options:")
        print("1. Use Ability")
        print("2. Refresh Character")
        print("3. Save & Exit")

        choice = input("> ").strip()

        if choice == "1":
            if not character.abilities:
                print("No abilities available.")
                continue

            print("Available Abilities:")
            for i, ability in enumerate(character.abilities, 1):
                print(f"{i}. {ability.name}")

            ability_choice = input("Choose ability #: ").strip()

            if ability_choice.isdigit():
                index = int(ability_choice) - 1
                if 0 <= index < len(character.abilities):
                    ability = character.abilities[index]

                    try:
                        execute_ability(character, ability.name)
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Invalid selection.")
            else:
                print("Invalid input.")

        elif choice == "2":
            from domain.calculations import recalculate
            recalculate(character)
            print("Character recalculated.")

        elif choice == "3":
            break

        else:
            print("Invalid option.")

    # -------------------------
    # SAVE CHARACTER
    # -------------------------

    os.makedirs(PERSISTENCE_DIR, exist_ok=True)

    filename = f"{char_name.replace(' ', '_').lower()}_character.json"
    filepath = os.path.join(PERSISTENCE_DIR, filename)

    data = character.to_dict()

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Character saved to: {filename}")


# -------------------------
# ENTRY POINT
# -------------------------

if __name__ == "__main__":
    main()
