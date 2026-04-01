import json, os

from application.character_creation import create_character, MATERIAL_EFFECTS
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.race import resolve_race, get_all_races, RACES
from domain.adventure import get_jobs_grouped_by_class, resolve_job
from domain.profession import get_all_professions, resolve_profession
from domain.effects import StatIncrease
from application.runtime import execute_ability
from domain.calculations import recalculate
from domain.content_registry import initialize_content_registries

initialize_content_registries()

PERSISTENCE_DIR = "src/persistence"

# HELPERS

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

# RACE SELECTION

def choose_race():
    races = get_all_races()

    print("Available races:")
    race_lookup = {}

    for race in RACES.values():
        print(f"- {race.name}")
        race_lookup[race.name.lower()] = race.name

    race_input = choose_from_mapping("Choose a race: ", race_lookup)
    race = resolve_race(race_input)

    base_race = None
    material = None

    if race.requires_material:
        print("\nThis race requires a base race and material.")

        # Base race selection
        base_candidates = [r for r in races if r.can_be_base]

        base_lookup = {}
        print("\nAvailable base races:")
        for r in base_candidates:
            print(f"- {r.name}")
            base_lookup[r.name.lower()] = r.name

        base_name = choose_from_mapping("Choose base race: ", base_lookup)
        base_race = resolve_race(base_name)

        # Material selection
        print("\nAvailable materials:")
        material_lookup = {m.lower(): m for m in MATERIAL_EFFECTS}

        for mat in MATERIAL_EFFECTS:
            print(f"- {mat}")

        material = choose_from_mapping("Choose material: ", material_lookup)

    return race, base_race, material

# JOB SELECTION

def choose_job():
    jobs_by_class = get_jobs_grouped_by_class()

    print("Available Jobs:")
    valid_jobs = {}

    for job_class in sorted(jobs_by_class):
        print(f"{job_class}:")
        for job in jobs_by_class[job_class]:
            bonuses = format_effects(job.effects_on_acquire)
            print(f"  - {job.name} ({bonuses})")
            valid_jobs[job.name.lower()] = job.name

    job_input = choose_from_mapping("Choose a job: ", valid_jobs)
    return resolve_job(job_input)

# PROFESSION SELECTION

def choose_profession():
    professions = get_all_professions()

    print("Available Professions:")
    valid = {}

    for prof in professions:
        bonuses = format_effects(prof.effects_on_acquire)
        print(f"- {prof.name} ({bonuses})")
        valid[prof.name.lower()] = prof.name

    choice = choose_from_mapping("Choose a profession: ", valid)
    return resolve_profession(choice)

# CHARACTER CREATION

def build_character():
    print("=== Generica Offline Character Creator ===\n")

    name = input("Enter character name: ").strip()
    while not name:
        name = input("Please enter a valid name: ").strip()

    race, base_race, material = choose_race()
    job = choose_job()
    profession = choose_profession()

    character = create_character(
        name,
        race=race,
        jobs=[job],
        professions=[profession],
        base_race=base_race,
        material=material,
    )

    print("=== Character Created ===")
    return character

# ABILITY HANDLING

def handle_ability_use(character):
    if not character.abilities:
        print("No abilities available.")
        return

    print("Available Abilities:")
    for i, ability in enumerate(character.abilities, 1):
        print(f"{i}. {ability.name}")

    choice = input("Choose ability #: ").strip()

    if not choice.isdigit():
        print("Invalid input.")
        return

    idx = int(choice) - 1

    if not (0 <= idx < len(character.abilities)):
        print("Invalid selection.")
        return

    ability = character.abilities[idx]

    try:
        execute_ability(character, ability.name)
    except Exception as e:
        print(f"Error: {e}")

# LOOP

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

# SAVE

def save_character(character):
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)

    filename = f"{character.name.replace(' ', '_').lower()}_character.json"
    path = os.path.join(PERSISTENCE_DIR, filename)

    with open(path, "w") as f:
        json.dump(character.to_dict(), f, indent=4)

    print(f"Character saved to: {filename}")

# ENTRY

def run_cli():
    character = build_character()

    should_save = interaction_loop(character)

    if should_save:
        save_character(character)
    else:
        print("Exited without saving.")
