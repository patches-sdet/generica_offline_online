from application.character_creation import apply_generic_skill_allocation, create_character
from application.leveling import level_up_progression
from domain.calculations import recalculate
from domain.content_registry import (
    get_all_adventure_jobs,
    get_all_base_races,
    get_all_profession_jobs,
    get_all_race_templates,
)
from domain.race_resolution import MATERIAL_EFFECTS
from presentation.character_sheet import ATTRIBUTE_NAMES

from .constants import (
    CREATION_ADVENTURE_LEVELS,
    CREATION_ATTRIBUTE_POINTS,
    CREATION_PROFESSION_LEVELS,
    CREATION_SKILL_POINTS,
    GENERIC_SKILL_NAMES,
)
from .presentation import print_job_options, print_named_options
from .prompts import choose_from_mapping, confirm, prompt_int, prompt_nonempty


def get_known_skill_names():
    return sorted(GENERIC_SKILL_NAMES)


def get_adventure_job_lookup():
    return {job.name.lower(): job.name for job in get_all_adventure_jobs()}


def get_profession_lookup():
    return {prof.name.lower(): prof.name for prof in get_all_profession_jobs()}


def choose_race_setup():
    base_races = get_all_base_races()
    race_templates = get_all_race_templates()

    print_named_options("Available base races:", [race.name for race in base_races])
    base_lookup = {race.name.lower(): race.name for race in base_races}

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

    name = prompt_nonempty("Enter character name: ", "Please enter a valid name: ")

    base_race_names, race_template_name, material = choose_race_setup()

    adventure_allocations = allocate_total_levels(
        "adventure job",
        CREATION_ADVENTURE_LEVELS,
        get_adventure_job_lookup(),
        lambda: print_job_options("Available Adventure Jobs:", get_all_adventure_jobs()),
    )

    profession_allocations = allocate_total_levels(
        "profession",
        CREATION_PROFESSION_LEVELS,
        get_profession_lookup(),
        lambda: print_job_options("Available Professions:", get_all_profession_jobs()),
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
