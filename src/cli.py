from application.character_creation import create_character
from presentation.character_sheet import debug_print_character
from domain.race import RACES
from domain.adventure import get_jobs_grouped_by_class

def run():
    print("=== Tabletop RPG Character Creator ===\n")

    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    print("\nAvailable races:")
    for race_name in RACES.keys():
        print(f"- {race_name}")

    race_name = input("\nChoose a race: ").strip()
    while race_name not in RACES:
        race_name = input("Invalid race: ").strip()

    jobs_by_class = get_jobs_grouped_by_class()

    print("\nAvailable jobs:")
    valid_jobs = []

    for job_class, jobs in jobs_by_class.items():
        print(f"\n{job_class}:")
        for job in jobs:
            bonuses = ", ".join(
                f"+{v} {k[:3].upper()}" for k, v in job.stat_modifiers.items()
            )
            print(f"  - {job.name} ({bonuses})")
            valid_jobs.append(job.name.lower())

    while True:
        job_name = input("\nChoose a job: ").strip()
        if job_name.lower() in valid_jobs:
            break
        print("Invalid job.")

    character = create_character(char_name, race_name, job_name)

    print("\n=== Character Created ===\n")
    debug_print_character(character)
