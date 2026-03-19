import json, os
from application.character_creation import create_character
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.race import RACES
from domain.adventure import get_jobs_grouped_by_class, get_all_jobs
from domain.effects import StatIncrease

PERSISTENCE_DIR = "src/persistence"

def format_effects(effects):
    parts = []

    for effect in effects:
        if isinstance(effect, StatIncrease):
            stat_name = ATTRIBUTE_NAMES.get(effect.stat, effect.stat.upper())
            parts.append(f"+{effect.amount} {stat_name}")

    return ", ".join(parts)

def main():
    print("=== Tabletop RPG Character Creator ===\n")

    # Ask for the character name
    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    # Display available races
    print("\nAvailable races:")
    for race_name in RACES.keys():
        print(f"- {race_name}")

    # Ask for the race choice
    race_name = input("\nChoose a race from the list above: ").strip()
    while race_name not in RACES:
        race_name = input("Invalid race. Please choose a valid race: ").strip()

    # Show available jobs, organized by class
    jobs_by_class = get_jobs_grouped_by_class()
    print("Available Jobs:")
    valid_jobs = []

    for job_class in sorted(jobs_by_class.keys()):
        print(f"{job_class}:")
        for job in jobs_by_class[job_class]:
            bonuses = format_effects(job.effects_on_acquire)
            print(f"  - {job.name} ({bonuses})")

            valid_jobs.append(job.name.lower())

    # input validation
    while True:
        job_name = input("Choose a job: ").strip()
        if job_name.lower() in valid_jobs:
            break
        print ("Invalid job. Please choose from the list.")

    # Create the character using character_creation.py
    character = create_character(char_name, race_name, job_name)

    # Print the character sheet
    print("\n=== Character Created ===\n")
    debug_print_character(character)

    os.makedirs(PERSISTENCE_DIR, exist_ok=True)
    filename = f"{char_name.replace(' ', '_').lower()}_character.json"
    filepath = os.path.join(PERSISTENCE_DIR, filename)

    data = character.to_dict()
    data.pop("pool_manager", None)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
        print(f"\nCharacter saved to: {filename}")

# sanity check test
# char = create_character("Test", "Human", "Archer")
# print("Job:", char.job.name)
# print("STR:", char.attributes.strength)

if __name__ == "__main__":
    main()
