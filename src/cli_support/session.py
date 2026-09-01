import json
import os

from application.runtime import execute_ability
from domain.calculations import recalculate
from presentation.character_sheet import debug_print_character

from .advancement import handle_leveling_menu
from .constants import PERSISTENCE_DIR
from .creation import build_character
from .presentation import print_active_abilities
from .prompts import confirm


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

    print_active_abilities(active_abilities)
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
    except Exception as error:
        print(f"Error: {error}")


def interaction_loop(character):
    should_save = False
    actions = {
        "1": lambda: handle_ability_use(character),
        "2": lambda: _rebuild_character(character),
        "3": lambda: handle_leveling_menu(character),
    }

    while True:
        debug_print_character(character)

        print("Options:")
        print("1. Use Ability")
        print("2. Rebuild Character State")
        print("3. Leveling / Advancement")
        print("4. Save & Exit")
        print("5. Exit Without Saving")

        choice = input("> ").strip()

        if choice == "4":
            should_save = True
            break

        if choice == "5":
            if confirm("Exit without saving? (y/n): "):
                break
            continue

        action = actions.get(choice)
        if action is None:
            print("Invalid option.")
            continue

        action()

    return should_save


def _rebuild_character(character):
    recalculate(character)
    print("Character rebuilt.")


def save_character(character):
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)

    filename = f"{character.name.replace(' ', '_').lower()}_character.json"
    path = os.path.join(PERSISTENCE_DIR, filename)

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(character.to_dict(), handle, indent=4)

    print(f"Character saved to: {path}")


def run_cli():
    character = build_character()

    should_save = interaction_loop(character)

    if should_save:
        save_character(character)
    else:
        print("Exited without saving.")
