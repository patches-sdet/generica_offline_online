from application.character_creation import apply_generic_skill_allocation
from application.leveling import (
    award_grind_points,
    award_level_points,
    grind_attribute,
    grind_skill,
    learn_new_advanced_job,
    learn_new_adventure_job,
    level_advanced_job,
    level_adventure_job,
    level_profession_job,
    level_race_progression,
)
from domain.calculations import recalculate
from domain.content_registry import get_all_advanced_jobs, get_all_adventure_jobs
from presentation.character_sheet import ATTRIBUTE_NAMES

from .creation import get_adventure_job_lookup, get_known_skill_names
from .presentation import print_attribute_values, print_job_options, print_progressions
from .prompts import choose_from_mapping, prompt_int


def choose_progression_by_type(character, ptype):
    progressions = character.get_progressions_by_type(ptype)

    if not progressions:
        print(f"No {ptype} progressions available.")
        return None

    print_progressions(f"Available {ptype} progressions:", progressions)
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


def _run_action(action):
    try:
        action()
    except Exception as error:
        print(f"Error: {error}")


def handle_level_adventure(character):
    progression = choose_progression_by_type(character, "adventure")
    if progression is not None:
        _run_action(lambda: level_adventure_job(character, progression.name))


def handle_level_profession(character):
    progression = choose_progression_by_type(character, "profession")
    if progression is not None:
        _run_action(lambda: level_profession_job(character, progression.name))


def handle_level_race(character):
    progression = choose_progression_by_type(character, "race")
    if progression is not None:
        _run_action(lambda: level_race_progression(character, progression.name))


def handle_level_advanced(character):
    progression = choose_progression_by_type(character, "advanced")
    if progression is not None:
        _run_action(lambda: level_advanced_job(character, progression.name))


def handle_learn_new_adventure(character):
    print_job_options("Available Adventure Jobs:", get_all_adventure_jobs())
    job_name = choose_from_mapping(
        "Choose new adventure job: ",
        get_adventure_job_lookup(),
    )
    _run_action(lambda: learn_new_adventure_job(character, job_name))


def handle_learn_new_advanced(character):
    print_job_options("Available Advanced Jobs:", get_all_advanced_jobs(), include_effects=False)
    job_lookup = {job.name.lower(): job.name for job in get_all_advanced_jobs()}
    job_name = choose_from_mapping("Choose new advanced job: ", job_lookup)
    _run_action(lambda: learn_new_advanced_job(character, job_name))


def handle_grind_skill(character):
    if not character.skill_levels:
        print("Character has no skills to grind.")
        return

    print("Current skills:")
    skills = sorted(character.skill_levels.items())

    for index, (skill_name, level) in enumerate(skills, 1):
        print(f"{index}. {skill_name} Lv. {level}")

    idx = prompt_int("Choose skill #: ", minimum=1, maximum=len(skills)) - 1
    skill_name = skills[idx][0]
    _run_action(lambda: grind_skill(character, skill_name))


def handle_grind_attribute(character):
    stats = print_attribute_values(character)
    idx = prompt_int("Choose attribute #: ", minimum=1, maximum=len(stats)) - 1
    stat = stats[idx]
    _run_action(lambda: grind_attribute(character, stat))


def handle_free_table_attribute_award(character):
    stats = print_attribute_values(character)
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
    actions = {
        "1": lambda: handle_award_level_points(character),
        "2": lambda: handle_award_grind_points(character),
        "3": lambda: handle_level_adventure(character),
        "4": lambda: handle_level_profession(character),
        "5": lambda: handle_level_race(character),
        "6": lambda: handle_level_advanced(character),
        "7": lambda: handle_learn_new_adventure(character),
        "8": lambda: handle_learn_new_advanced(character),
        "9": lambda: handle_grind_skill(character),
        "10": lambda: handle_grind_attribute(character),
        "11": lambda: handle_free_table_attribute_award(character),
        "12": lambda: handle_free_table_skill_award(character),
    }

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
        if choice == "13":
            return

        action = actions.get(choice)
        if action is None:
            print("Invalid option.")
            continue

        action()
