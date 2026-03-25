```python
from application.character_creation import create_character
from presentation.character_sheet import debug_print_character, ATTRIBUTE_NAMES
from domain.race import RACES, resolve_race
from domain.adventure import get_jobs_grouped_by_class
from domain.profession import get_all_professions
from domain.effects import StatIncrease
from domain.materials import MATERIAL_EFFECTS


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


def choose_from_mapping(prompt, options_dict):
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_dict:
            return options_dict[choice]
        print("Invalid choice. Try again.")


# -------------------------
# CLI ENTRY
# -------------------------

def run():
    print("=== Tabletop RPG Character Creator ===\n")

    # Name
    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    # -------------------------
    # Race
    # -------------------------

    print("\nAvailable races:")
    for race in sorted(RACES.keys()):
        print(f"- {race}")

    race_lookup = {r.lower(): r for r in RACES.keys()}

    race = choose_from_mapping("Choose a race: ", race_lookup)
    race = resolve_race(race)

    base_race = None
    material = None

    if race.requires_material:
        print("\nThis race requires a base race and material.")

        base_race_lookup = {
            r.name.lower(): r.name
            for r in RACES.values()
            if not r.requires_material
        }

        print("\nAvailable base races:")
        for name in base_race_lookup.values():
            print(f"- {name}")

        base_race = choose_from_mapping(
            "Choose base race: ",
            base_race_lookup
        )

        material_lookup = {m.lower(): m for m in MATERIAL_EFFECTS.keys()}

        print("\nAvailable materials:")
        for mat in MATERIAL_EFFECTS.keys():
            print(f"- {mat}")

        material = choose_from_mapping(
            "Choose material: ",
            material_lookup
        )

    # -------------------------
    # Job
    # -------------------------

    jobs_by_class = get_jobs_grouped_by_class()
    print("\nAvailable Jobs:")

    valid_jobs = {}

    for job_class in sorted(jobs_by_class.keys()):
        print(f"{job_class}:")
        for job in jobs_by_class[job_class]:
            bonuses = format_effects(job.effects_on_acquire)
            print(f"  - {job.name} ({bonuses})")
            valid_jobs[job.name.lower()] = job.name

    job = choose_from_mapping("Choose a job: ", valid_jobs)

    # -------------------------
    # Profession
    # -------------------------

    professions = get_all_professions()

    print("\nAvailable Professions:")
    valid_professions = {}

    for prof in professions:
        bonuses = format_effects(prof.effects_on_acquire)
        print(f"- {prof.name} ({bonuses})")
        valid_professions[prof.name.lower()] = prof.name

    profession = choose_from_mapping(
        "Choose a profession: ",
        valid_professions
    )

    # -------------------------
    # Create + Display
    # -------------------------

    character = create_character(
        char_name,
        race,
        job,
        profession,
        base_race=base_race,
        material=material
    )

    print("\n=== Character Created ===\n")
    debug_print_character(character)
```

